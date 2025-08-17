import logging
from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_core.documents import Document
import chardet
from langchain_core.document_loaders import BaseLoader

class ListLoader(BaseLoader):
   """A wrapper to make a list of Documents compatible with BaseLoader."""
   def __init__(self, documents):
       self.documents = documents
   def load(self):
       return self.documents
   
def detect_encoding(file_path):
   """Detects the file encoding to avoid UnicodeDecodeError."""
   with open(file_path, 'rb') as f:
       raw_data = f.read(4096)
       result = chardet.detect(raw_data)
       return result['encoding'] or "utf-8"
   
def load_document_content(file_path):
    file_extension = Path(file_path).suffix.lower()
    encoding_flag = False
    if file_extension == '.pdf':
        loader = PyMuPDFLoader(file_path)
        return loader,encoding_flag
    elif file_extension == ".txt":
        encoding = detect_encoding(file_path)
        logging.info(f"Detected encoding for {file_path}: {encoding}")
        if encoding.lower() == "utf-8":
            loader = UnstructuredFileLoader(file_path, mode="elements",autodetect_encoding=True)
            return loader,encoding_flag
        else:
            with open(file_path, encoding=encoding, errors="replace") as f:
               content = f.read()
            loader = ListLoader([Document(page_content=content, metadata={"source": file_path})])
            encoding_flag =  True
            return loader,encoding_flag
    else:
        loader = UnstructuredFileLoader(file_path, mode="elements",autodetect_encoding=True)
        return loader,encoding_flag
    
def get_documents_from_file_by_path(file_path,file_name):
    file_path = Path(file_path)
    if not file_path.exists():
        logging.info(f'❌ File {file_name} does not exist')
        raise Exception(f'File {file_name} does not exist')
    
    logging.info("=" * 60)
    logging.info("📁 STARTING LOCAL FILE LOADING")
    logging.info("=" * 60)
    logging.info(f"📁 File path: {file_path}")
    logging.info(f"📄 File name: {file_name}")
    logging.info(f"🔧 File extension: {file_path.suffix.lower()}")
    logging.info(f"📏 File size: {file_path.stat().st_size} bytes")
    
    try:
        loader, encoding_flag = load_document_content(file_path)
        file_extension = file_path.suffix.lower()
        logging.info(f"✅ Loader created successfully")
        logging.info(f"🔧 Encoding flag: {encoding_flag}")
        logging.info(f"🔧 Loader type: {type(loader).__name__}")
        
        if file_extension == ".pdf" or (file_extension == ".txt" and encoding_flag):
            logging.info(f"📖 Loading PDF/TXT with structured loader...")
            pages = loader.load()
            logging.info(f"📄 Raw pages loaded: {len(pages)}")
            
            # Additional validation for PDFs
            if file_extension == ".pdf" and len(pages) == 0:
                logging.error(f"❌ PDF loader returned 0 pages. This might indicate:")
                logging.error(f"   - PDF is corrupted or password-protected")
                logging.error(f"   - PDF parsing library issue")
                logging.error(f"   - File is empty or invalid")
                raise Exception(f"PDF loader failed to extract any pages from {file_name}")
                
        else:
            logging.info(f"📄 Loading unstructured document...")
            unstructured_pages = loader.load()
            logging.info(f"📄 Unstructured pages loaded: {len(unstructured_pages)}")
            pages = get_pages_with_page_numbers(unstructured_pages)
        
        logging.info(f"✅ File loading completed!")
        logging.info(f"📄 Total pages loaded: {len(pages)}")
        
        # Log details about each page
        for i, page in enumerate(pages):
            logging.info(f"   📄 Page {i+1}: {len(page.page_content)} characters")
            if hasattr(page, 'metadata') and 'page_number' in page.metadata:
                logging.info(f"      📊 Page number: {page.metadata['page_number']}")
        
        # Final validation
        if len(pages) == 0:
            logging.error(f"❌ CRITICAL: No pages extracted from file {file_name}")
            raise Exception(f"No content could be extracted from {file_name}. File may be corrupted or empty.")
        
        logging.info("=" * 60)
        return file_name, pages, file_extension
        
    except Exception as e:
        logging.error(f"❌ File loading failed: {str(e)}")
        logging.error(f"❌ Exception type: {type(e).__name__}")
        logging.error(f"❌ File details: {file_path}, size: {file_path.stat().st_size if file_path.exists() else 'N/A'} bytes")
        raise Exception(f'Error while reading the file content or metadata, {e}')

def get_pages_with_page_numbers(unstructured_pages):
    pages = []
    page_number = 1
    page_content=''
    metadata = {}
    for page in unstructured_pages:
        if  'page_number' in page.metadata:
            if page.metadata['page_number']==page_number:
                page_content += page.page_content
                metadata = {'source':page.metadata['source'],'page_number':page_number, 'filename':page.metadata['filename'],
                        'filetype':page.metadata['filetype']}
                
            if page.metadata['page_number']>page_number:
                page_number+=1
                pages.append(Document(page_content = page_content))
                page_content='' 
                
            if page == unstructured_pages[-1]:
                pages.append(Document(page_content = page_content))
                    
        elif page.metadata['category']=='PageBreak' and page!=unstructured_pages[0]:
            page_number+=1
            pages.append(Document(page_content = page_content, metadata=metadata))
            page_content=''
            metadata={}
        
        else:
            page_content += page.page_content
            metadata_with_custom_page_number = {'source':page.metadata['source'],
                            'page_number':1, 'filename':page.metadata['filename'],
                            'filetype':page.metadata['filetype']}
            if page == unstructured_pages[-1]:
                    pages.append(Document(page_content = page_content, metadata=metadata_with_custom_page_number))
    return pages                
