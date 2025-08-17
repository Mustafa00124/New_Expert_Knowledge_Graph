import logging
from neo4j import time 
from neo4j import GraphDatabase
import os
import json

from src.shared.constants import GRAPH_CHUNK_LIMIT,GRAPH_QUERY,CHUNK_TEXT_QUERY,COUNT_CHUNKS_QUERY,SCHEMA_VISUALIZATION_QUERY, CHUNK_TEXT_OFFSET

def get_graphDB_driver(uri, username, password,database="neo4j"):
    """
    Creates and returns a Neo4j database driver instance configured with the provided credentials.

    Returns:
    Neo4j.Driver: A driver object for interacting with the Neo4j database.

    """
    try:
        logging.info(f"Attempting to connect to the Neo4j database at {uri}")
        if all(v is None for v in [username, password]):
            username= os.getenv('NEO4J_USERNAME')
            database= os.getenv('NEO4J_DATABASE')
            password= os.getenv('NEO4J_PASSWORD')

        enable_user_agent = os.environ.get("ENABLE_USER_AGENT", "False").lower() in ("true", "1", "yes")
        if enable_user_agent:
            driver = GraphDatabase.driver(uri, auth=(username, password),database=database, user_agent=os.environ.get('NEO4J_USER_AGENT'))
        else:
            driver = GraphDatabase.driver(uri, auth=(username, password),database=database)
        logging.info("Connection successful")
        return driver
    except Exception as e:
        error_message = f"graph_query module: Failed to connect to the database at {uri}."
        logging.error(error_message, exc_info=True)


def execute_query(driver, query,document_names,doc_limit=None):
    """
    Executes a specified query using the Neo4j driver, with parameters based on the presence of a document name.

    Returns:
    tuple: Contains records, summary of the execution, and keys of the records.
    """
    try:
        if document_names:
            logging.info(f"Executing query for documents: {document_names}")
            records, summary, keys = driver.execute_query(query, document_names=document_names)
        else:
            logging.info(f"Executing query with a document limit of {doc_limit}")
            records, summary, keys = driver.execute_query(query, doc_limit=doc_limit)
        return records, summary, keys
    except Exception as e:
        error_message = f"graph_query module: Failed to execute the query. Error: {str(e)}"
        logging.error(error_message, exc_info=True)


def process_node(node):
    """
    Processes a node from a Neo4j database, extracting its ID, labels, and properties,
    while omitting certain properties like 'embedding' and 'text'.

    Returns:
    dict: A dictionary with the node's element ID, labels, and other properties,
          with datetime objects formatted as ISO strings.
    """
    try:
        labels = set(node.labels)
        labels.discard("__Entity__")
        if not labels:
            labels.add('*')
        
        node_element = {
            "element_id": node.element_id,
            "labels": list(labels),
            "properties": {}
        }
        # logging.info(f"Processing node with element ID: {node.element_id}")

        for key in node:
            if key in ["embedding", "text", "summary"]:
                continue
            value = node.get(key)
            if isinstance(value, time.DateTime):
                node_element["properties"][key] = value.isoformat()
                # logging.debug(f"Processed datetime property for {key}: {value.isoformat()}")
            else:
                node_element["properties"][key] = value

        return node_element
    except Exception as e:
        logging.error("graph_query module:An unexpected error occurred while processing the node")

def extract_node_elements(records):
    """
    Extracts and processes unique nodes from a list of records, avoiding duplication by tracking seen element IDs.

    Returns:
    list of dict: A list containing processed node dictionaries.
    """
    node_elements = []
    seen_element_ids = set()  

    try:
        for record in records:
            nodes = record.get("nodes", [])
            if not nodes:
                # logging.debug(f"No nodes found in record: {record}")
                continue

            for node in nodes:
                if node.element_id in seen_element_ids:
                    # logging.debug(f"Skipping already processed node with ID: {node.element_id}")
                    continue
                seen_element_ids.add(node.element_id)
                node_element = process_node(node) 
                node_elements.append(node_element)
                # logging.info(f"Processed node with ID: {node.element_id}")

        return node_elements
    except Exception as e:
        logging.error("graph_query module: An error occurred while extracting node elements from records")

def extract_relationships(records):
    """
    Extracts and processes relationships from a list of records, ensuring that each relationship is processed
    only once by tracking seen element IDs.

    Returns:
    list of dict: A list containing dictionaries of processed relationships.
    """
    all_relationships = []
    seen_element_ids = set()

    try:
        for record in records:
            relationships = []
            relations = record.get("rels", [])
            if not relations:
                continue

            for relation in relations:
                if relation.element_id in seen_element_ids:
                    # logging.debug(f"Skipping already processed relationship with ID: {relation.element_id}")
                    continue
                seen_element_ids.add(relation.element_id)

                try:
                    nodes = relation.nodes
                    if len(nodes) < 2:
                        logging.warning(f"Relationship with ID {relation.element_id} does not have two nodes.")
                        continue

                    relationship = {
                        "element_id": relation.element_id,
                        "type": relation.type,
                        "start_node_element_id": process_node(nodes[0])["element_id"],
                        "end_node_element_id": process_node(nodes[1])["element_id"],
                    }
                    relationships.append(relationship)

                except Exception as inner_e:
                    logging.error(f"graph_query module: Failed to process relationship with ID {relation.element_id}. Error: {inner_e}", exc_info=True)
            all_relationships.extend(relationships)
        return all_relationships
    except Exception as e:
        logging.error("graph_query module: An error occurred while extracting relationships from records", exc_info=True)


def get_completed_documents(driver):
    """
    Retrieves the names of all documents with the status 'Completed' from the database.
    """
    docs_query = "MATCH(node:Document {status:'Completed'}) RETURN node"
    
    try:
        logging.info("Executing query to retrieve completed documents.")
        records, summary, keys = driver.execute_query(docs_query)
        logging.info(f"Query executed successfully, retrieved {len(records)} records.")
        documents = [record["node"]["fileName"] for record in records]
        logging.info("Document names extracted successfully.")
        
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        documents = []
    
    return documents


def get_graph_results(uri, username, password,database,document_names):
    """
    Retrieves graph data by executing a specified Cypher query using credentials and parameters provided.
    Processes the results to extract nodes and relationships and packages them in a structured output.

    Args:
    uri (str): The URI for the Neo4j database.
    username (str): The username for authentication.
    password (str): The password for authentication.
    query_type (str): The type of query to be executed.
    document_name (str, optional): The name of the document to specifically query for, if any. Default is None.

    Returns:
    dict: Contains the session ID, user-defined messages with nodes and relationships, and the user module identifier.
    """
    try:
        logging.info("=" * 80)
        logging.info("🔍 STARTING GRAPH QUERY")
        logging.info("=" * 80)
        logging.info(f"📁 Document names: {document_names}")
        logging.info(f"⚙️  GRAPH_CHUNK_LIMIT: {GRAPH_CHUNK_LIMIT}")
        
        driver = get_graphDB_driver(uri, username, password,database)  
        document_names= list(map(str, json.loads(document_names)))
        query = GRAPH_QUERY.format(graph_chunk_limit=GRAPH_CHUNK_LIMIT)
        
        logging.info(f"🔍 Executing graph query with limit: {GRAPH_CHUNK_LIMIT}")
        records, summary , keys = execute_query(driver, query.strip(), document_names)
        
        logging.info(f"📊 Query execution completed")
        logging.info(f"📄 Records returned: {len(records)}")
        logging.info(f"🔑 Keys: {keys}")
        
        document_nodes = extract_node_elements(records)
        document_relationships = extract_relationships(records)

        logging.info(f"📊 GRAPH QUERY RESULTS:")
        logging.info(f"   🎯 Nodes extracted: {len(document_nodes)}")
        logging.info(f"   🔗 Relationships extracted: {len(document_relationships)}")
        
        # Log node type distribution
        node_types = {}
        for node in document_nodes:
            if 'labels' in node:
                for label in node['labels']:
                    node_types[label] = node_types.get(label, 0) + 1
        
        if node_types:
            logging.info(f"   📊 Node type distribution:")
            for label, count in node_types.items():
                logging.info(f"      {label}: {count}")
        
        # Log relationship type distribution
        rel_types = {}
        for rel in document_relationships:
            if 'type' in rel:
                rel_type = rel['type']
                rel_types[rel_type] = rel_types.get(rel_type, 0) + 1
        
        if rel_types:
            logging.info(f"   📊 Relationship type distribution:")
            for rel_type, count in rel_types.items():
                logging.info(f"      {rel_type}: {count}")
        
        result = {
            "nodes": document_nodes,
            "relationships": document_relationships
        }

        logging.info(f"✅ Graph query process completed successfully")
        logging.info("=" * 80)
        return result
    except Exception as e:
        logging.error(f"❌ Graph query failed: {str(e)}")
        logging.error(f"graph_query module: An error occurred in get_graph_results. Error: {str(e)}")
        raise Exception(f"graph_query module: An error occurred in get_graph_results. Please check the logs for more details.") from e
    finally:
        logging.info("🔌 Closing connection for graph_query api")
        driver.close()


def get_chunktext_results(uri, username, password, database, document_name, page_no):
   """Retrieves chunk text, position, and page number from graph data with pagination."""
   driver = None
   try:
       logging.info("=" * 60)
       logging.info("📄 STARTING CHUNK TEXT QUERY")
       logging.info("=" * 60)
       logging.info(f"📁 Document: {document_name}")
       logging.info(f"📄 Page number: {page_no}")
       logging.info(f"⚙️  CHUNK_TEXT_OFFSET: {CHUNK_TEXT_OFFSET}")
       
       offset = CHUNK_TEXT_OFFSET  # Use configurable constant instead of hard-coded value
       skip = (page_no - 1) * offset
       limit = offset
       
       logging.info(f"📊 Pagination settings:")
       logging.info(f"   ➡️  Offset: {offset}")
       logging.info(f"   ➡️  Skip: {skip}")
       logging.info(f"   ➡️  Limit: {limit}")
       
       driver = get_graphDB_driver(uri, username, password,database)  
       with driver.session(database=database) as session:
           logging.info("🔍 Getting total chunk count...")
           total_chunks_result = session.run(COUNT_CHUNKS_QUERY, file_name=document_name)
           total_chunks = total_chunks_result.single()["total_chunks"]
           total_pages = (total_chunks + offset - 1) // offset  # Calculate total pages
           
           logging.info(f"📊 Total chunks in document: {total_chunks}")
           logging.info(f"📄 Total pages available: {total_pages}")
           
           logging.info(f"🔍 Executing chunk text query...")
           records = session.run(CHUNK_TEXT_QUERY, file_name=document_name, skip=skip, limit=limit)
           
           pageitems = [
               {
                   "text": record["chunk_text"],
                   "position": record["chunk_position"],
                   "pagenumber": record["page_number"]
               }
               for record in records
           ]
           
           logging.info(f"✅ Chunk text query completed successfully")
           logging.info(f"📊 Results for page {page_no}:")
           logging.info(f"   ➡️  Chunks retrieved: {len(pageitems)}")
           logging.info(f"   ➡️  Total chunks: {total_chunks}")
           logging.info(f"   ➡️  Total pages: {total_pages}")
           
           # Log chunk details
           for i, item in enumerate(pageitems):
               logging.info(f"      📄 Chunk {i+1}: position {item['position']}, page {item['pagenumber']}, {len(item['text'])} chars")
           
           logging.info("=" * 60)
           return {
               "pageitems": pageitems,
               "total_pages": total_pages
           }
   except Exception as e:
       logging.error(f"❌ Chunk text query failed: {str(e)}")
       logging.error(f"An error occurred in get_chunktext_results. Error: {str(e)}")
       raise Exception("An error occurred in get_chunktext_results. Please check the logs for more details.") from e
   finally:
       if driver:
           logging.info("🔌 Closing database connection")
           driver.close()


def visualize_schema(uri, userName, password, database):
   """Retrieves graph schema"""
   driver = None
   try:
       logging.info("Starting visualizing graph schema")
       driver = get_graphDB_driver(uri, userName, password,database)  
       records, summary, keys = driver.execute_query(SCHEMA_VISUALIZATION_QUERY)
       nodes = records[0].get("nodes", [])
       relationships = records[0].get("relationships", [])
       result = {"nodes": nodes, "relationships": relationships}
       return result
   except Exception as e:
       logging.error(f"An error occurred schema retrieval. Error: {str(e)}")
       raise Exception(f"An error occurred schema retrieval. Error: {str(e)}")
   finally:
       if driver:
           driver.close()
