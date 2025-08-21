# Project Flow Documentation

This document explains the overall flow of the system and the main points where developers can make changes. The system consists of three key stages: **chunking**, **graph building**, and **question answering (QA)**. Each stage has its own logic file and offers two levels of control: quick adjustments via configuration and deeper modifications through code edits.

---

## Overall Flow

The process starts when a source document is uploaded. Sources can include local files (text, Word, PDF), YouTube transcripts, Wikipedia pages, or general web links.  

1. **Chunking**: The document is split into smaller chunks so it can be processed by the language model without losing context.  
2. **Graph Building**: The chunks are passed to an LLM that extracts entities and relationships, creating a structured knowledge graph.  
3. **QA Layer**: A chatbot queries this graph, retrieves the most relevant nodes, edges, and snippets, and uses an LLM to generate fluent answers.  

The graph is stored in Neo4j, which makes retrieval efficient and scalable. The overall orchestration lives in `main.py`.

---

## Chunking

**File**: `create_chunks.py`  

- The default splitter is **TokenTextSplitter**.  
- Key arguments:  
  - `chunk_size`: How much text goes into each chunk.  
  - `chunk_overlap`: How much content overlaps between chunks.  

**Configuration options**:  
- Adjust `chunk_size` and `chunk_overlap` for fine-tuning.  
- Swap TokenTextSplitter with another LangChain splitter such as:  
  - `RecursiveCharacterTextSplitter`: splits by paragraphs or sentences.  
  - `SemanticChunker`: splits based on meaning shifts.  
- Implement a custom splitter if you need specialized rules (e.g., by section headings or timestamps).  

**Summary**: Most adjustments can be done via configuration, but replacing or editing the splitter gives full control.

---

## Graph Building

**File**: `llm.py`  

- Uses **LLMGraphTransformer** to extract nodes and relationships.  
- Configurable settings:  
  - Allowed node types (`allowed_nodes`).  
  - Allowed relationships (`allowed_relationships`).  
  - Model choice and prompt style.  
  - Cost/latency tradeoffs.  

**Configuration options**:  
- Define node and edge types through config.  
- Adjust extraction behavior with arguments and prompts.  

**Code changes needed if**:  
- Adding new fields to nodes (confidence, provenance, timestamps).  
- Enforcing a strict ontology or schema.  
- Adding stronger post-processing (deduplication, coreference resolution, cross-chunk reasoning).  

**Summary**: Basic changes are handled in config, but structural changes require editing the transformer or pipeline.

---

## Question Answering (QA)

**File**: `qa_integration.py`  

- Uses **GraphCypherQAChain** to connect the chatbot with Neo4j.  
- Flow:  
  1. LLM translates natural language into a Cypher query.  
  2. Cypher query is executed on Neo4j.  
  3. Results are passed to another LLM for final answer generation.  

**Configuration options**:  
- Choose LLMs for Cypher generation and answering.  
- Adjust `top_k` (number of results).  
- Enable or disable query validation.  
- Return intermediate steps (Cypher query, context).  

**When to edit code**:  
- If you want **multi-step reasoning** with ReAct-style loops, where the Cypher LLM runs several queries and decides which context to send to the QA LLM.  
- For example, this can improve retrieval in complex graphs by iteratively refining context.  

**Summary**: Retrieval quality is the most important factor. Simple settings are configurable, but advanced iterative retrieval requires modifying the functions.

---