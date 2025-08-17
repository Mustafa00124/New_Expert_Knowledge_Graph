from langchain_community.document_loaders import WebBaseLoader
from src.shared.llm_graph_builder_exception import LLMGraphBuilderException
from src.shared.common_fn import last_url_segment
import logging

def get_documents_from_web_page(source_url:str):
  try:
    logging.info("=" * 60)
    logging.info("🌐 STARTING WEB PAGE LOADING")
    logging.info("=" * 60)
    logging.info(f"🔗 URL: {source_url}")
    
    pages = WebBaseLoader(source_url, verify_ssl=False).load()
    
    logging.info(f"✅ Web page loading completed!")
    logging.info(f"📄 Total pages loaded: {len(pages)}")
    
    # Log details about each page
    for i, page in enumerate(pages):
        logging.info(f"   📄 Page {i+1}: {len(page.page_content)} characters")
        if hasattr(page, 'metadata') and 'title' in page.metadata:
            logging.info(f"      📝 Title: {page.metadata['title']}")
        if hasattr(page, 'metadata') and 'language' in page.metadata:
            logging.info(f"      🌍 Language: {page.metadata['language']}")
    
    logging.info("=" * 60)
    return pages
  except Exception as e:
    logging.error(f"❌ Web page loading failed: {str(e)}")
    raise LLMGraphBuilderException(str(e))
