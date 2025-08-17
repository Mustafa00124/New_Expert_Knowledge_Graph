import logging
from langchain_community.document_loaders import WikipediaLoader
from src.shared.llm_graph_builder_exception import LLMGraphBuilderException
from src.shared.constants import MAX_WIKIPEDIA_DOCS

def get_documents_from_Wikipedia(wiki_query:str, language:str):
  try:
    logging.info("=" * 60)
    logging.info("🌐 STARTING WIKIPEDIA DOCUMENT LOADING")
    logging.info("=" * 60)
    logging.info(f"🔍 Query: {wiki_query}")
    logging.info(f"🌍 Language: {language}")
    logging.info(f"⚙️  Max docs to load: {MAX_WIKIPEDIA_DOCS}")
    logging.info(f"📏 Max content chars: 100,000")
    
    pages = WikipediaLoader(query=wiki_query.strip(), lang=language, load_all_available_meta=False,doc_content_chars_max=100000,load_max_docs=MAX_WIKIPEDIA_DOCS).load()
    file_name = wiki_query.strip()
    
    logging.info(f"✅ Wikipedia loading completed!")
    logging.info(f"📄 Total pages loaded: {len(pages)}")
    logging.info(f"📁 File name: {file_name}")
    
    # Log details about each page
    for i, page in enumerate(pages):
        logging.info(f"   📄 Page {i+1}: {len(page.page_content)} characters")
        if hasattr(page, 'metadata') and 'title' in page.metadata:
            logging.info(f"      📝 Title: {page.metadata['title']}")
    
    logging.info("=" * 60)
    return file_name, pages
  except Exception as e:
    message="Failed To Process Wikipedia Query"
    error_message = str(e)
    logging.error(f"❌ Wikipedia loading failed: {error_message}")
    logging.exception(f'Failed To Process Wikipedia Query, Exception Stack trace: {error_message}')
    raise LLMGraphBuilderException(error_message+' '+message)
  