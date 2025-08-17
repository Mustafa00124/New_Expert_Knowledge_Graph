from langchain_text_splitters import TokenTextSplitter
from langchain.docstore.document import Document
from langchain_neo4j import Neo4jGraph
import logging
from src.document_sources.youtube import get_chunks_with_timestamps, get_calculated_timestamps
import re
import os

logging.basicConfig(format="%(asctime)s - %(message)s", level="INFO")


class CreateChunksofDocument:
    def __init__(self, pages: list[Document], graph: Neo4jGraph):
        self.pages = pages
        self.graph = graph

    def split_file_into_chunks(self,token_chunk_size, chunk_overlap):
        """
        Split a list of documents(file pages) into chunks of fixed size.

        Args:
            pages: A list of pages to split. Each page is a list of text strings.

        Returns:
            A list of chunks each of which is a langchain Document.
        """
        logging.info("=" * 80)
        logging.info("🔄 STARTING CHUNK CREATION PROCESS")
        logging.info("=" * 80)
        logging.info(f"📄 Total pages received: {len(self.pages)}")
        logging.info(f"🔧 Token chunk size: {token_chunk_size}")
        logging.info(f"🔗 Chunk overlap: {chunk_overlap}")
        
        text_splitter = TokenTextSplitter(chunk_size=token_chunk_size, chunk_overlap=chunk_overlap)
        MAX_TOKEN_CHUNK_SIZE = int(os.getenv('MAX_TOKEN_CHUNK_SIZE', 100000))  # Updated default to match environment
        chunk_to_be_created = int(MAX_TOKEN_CHUNK_SIZE / token_chunk_size)
        
        logging.info(f"⚙️  MAX_TOKEN_CHUNK_SIZE from env: {MAX_TOKEN_CHUNK_SIZE}")
        logging.info(f"📊 Theoretical max chunks: {chunk_to_be_created}")
        
        if 'page' in self.pages[0].metadata:
            logging.info("📖 Processing PDF-like document with page metadata")
            chunks = []
            for i, document in enumerate(self.pages):
                page_number = i + 1
                logging.info(f"📄 Processing page {page_number}/{len(self.pages)}")
                # Remove the hard-coded limit to allow all pages to be processed
                page_chunks = text_splitter.split_documents([document])
                logging.info(f"   ➡️  Page {page_number} split into {len(page_chunks)} chunks")
                for chunk in page_chunks:
                    chunks.append(Document(page_content=chunk.page_content, metadata={'page_number':page_number}))
                logging.info(f"   ✅ Total chunks so far: {len(chunks)}")
        
        elif 'length' in self.pages[0].metadata:
            logging.info("🎥 Processing video/audio document with length metadata")
            if len(self.pages) == 1  or (len(self.pages) > 1 and self.pages[1].page_content.strip() == ''): 
                logging.info("🎬 Processing YouTube video")
                match = re.search(r'(?:v=)([0-9A-Za-z_-]{11})\s*',self.pages[0].metadata['source'])
                youtube_id=match.group(1)   
                chunks_without_time_range = text_splitter.split_documents([self.pages[0]])
                logging.info(f"   ➡️  YouTube content split into {len(chunks_without_time_range)} chunks")
                chunks = get_calculated_timestamps(chunks_without_time_range, youtube_id)  # Removed limit
                logging.info(f"   ✅ Final YouTube chunks with timestamps: {len(chunks)}")
            else: 
                logging.info("🎵 Processing audio/video with multiple segments")
                chunks_without_time_range = text_splitter.split_documents(self.pages)
                logging.info(f"   ➡️  Audio/video content split into {len(chunks_without_time_range)} chunks")
                chunks = get_calculated_timestamps(chunks_without_time_range)  # Removed limit
                logging.info(f"   ✅ Final audio/video chunks with timestamps: {len(chunks)}")
        else:
            logging.info("📄 Processing generic document without page metadata")
            chunks = text_splitter.split_documents(self.pages)
            logging.info(f"   ✅ Generic document split into {len(chunks)} chunks")
            
        # Only apply limit if it's absolutely necessary to prevent memory issues
        if len(chunks) > chunk_to_be_created * 10:  # Allow 10x more chunks than before
            logging.warning(f"⚠️  LIMITING CHUNKS: From {len(chunks)} to {chunk_to_be_created * 10} to prevent memory issues")
            chunks = chunks[:chunk_to_be_created * 10]
        
        logging.info("=" * 80)
        logging.info("📊 CHUNK CREATION SUMMARY")
        logging.info("=" * 80)
        logging.info(f"📄 Input pages: {len(self.pages)}")
        logging.info(f"🔧 Token chunk size: {token_chunk_size}")
        logging.info(f"🔗 Chunk overlap: {chunk_overlap}")
        logging.info(f"⚙️  Max token size: {MAX_TOKEN_CHUNK_SIZE}")
        logging.info(f"📊 Theoretical max chunks: {chunk_to_be_created}")
        logging.info(f"✅ Final chunks created: {len(chunks)}")
        logging.info(f"📈 Processing ratio: {len(chunks)/len(self.pages):.2f} chunks per page")
        logging.info("=" * 80)
        
        return chunks