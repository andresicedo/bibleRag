import logging
import tempfile
import pymupdf
import os
import time
import re
from typing import Dict, List
from werkzeug.datastructures import FileStorage
from pathlib import Path
from pymupdf import Document as pypdfDocument, Page as pypdfPage
from pymongo import collection, database
from llama_index.core.schema import TextNode
from src.models import RawDocument, BibleRequest, BibleReference, BibleMetadata
from src import config
from src.clients.mongo_client import get_bible_rag_db

LOG = logging.getLogger(__name__)
extensions: List[str] = ['.pdf']
BIBLE_VERSION: str = config.env_config.BIBLE_VERSION

def process_documents(bible_request: BibleRequest) -> List[RawDocument]:
    """Process the documents in the BibleRequest."""
    file_names: List[str] = [file.filename for file in bible_request.files]
    total_files: int = len(file_names)
    LOG.info(f"document_service: Processing {total_files} files STARTED: {file_names}")

    for file in bible_request.files:
        extracted_bible_data: List[RawDocument] = extract_file(file=file)
        LOG.info(f"document_service: Extracted {len(extracted_bible_data)} pages from {file.filename}")
    
    LOG.info(f"document_service: Processing COMPLETED for {file.filename}")
    return extracted_bible_data


def extract_file(file: FileStorage) -> List[RawDocument]:
    """Extract data from a file and return a list of RawDocuments."""
    if not file.filename:
        LOG.error("No file provided for extraction")
        raise ValueError("No file provided for extraction")
    
    if file and any(file.filename.lower().endswith(ext) for ext in extensions):
        LOG.info(f"Extracting data from file: {file.filename}")
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as temp_file:
                temp_path = temp_file.name
                temp_file.write(file.read())
                temp_file.flush()
                LOG.info(f"Temporary file created at: {temp_path}")

                bible_document: pypdfDocument = pymupdf.open(temp_path)

                if bible_document.page_count == 0:
                    raise ValueError("The document is empty or has no pages.")
                
                raw_bible: List[RawDocument] = []
                prev_book: str = "Genesis"
                prev_chapter: int = 1
                for page_number in range(74, bible_document.page_count): # Starting at index 74 as the first book starts here
                    pdf_page_number: int = page_number + 1  # Page numbers are 1-based in the PDF
                    pdf_page: pypdfPage = bible_document.load_page(page_number)
                    text: str = pdf_page.get_text("text").replace('\n', ' ')
                    raw_page: RawDocument = RawDocument(doc_id=pdf_page_number, doc_data=text)
                    tag_raw_document_with_metadata(raw_bible_page=raw_page, prev_book=prev_book, prev_chapter=prev_chapter)
                    raw_bible.append(raw_page)
                    prev_book = raw_page.metadata['book']
                    prev_chapter = raw_page.metadata['chapter']

                bible_document.close()
                return raw_bible
        except Exception as e:
            LOG.error(f"Error extracting file {file.filename}: {str(e)}")
            raise RuntimeError(f"Failed to extract file {file.filename}: {str(e)}")
        finally:
            delete_temp_file(temp_path)
    else:
        LOG.error(f"Unsupported file type: {file.filename}")
        raise ValueError(f"Unsupported file type: {file.filename}")


def delete_temp_file(temp_path):
    """Delete the temporary file if it exists."""
    LOG.debug(f"Attempting to delete temporary file: {temp_path}")
    if temp_path and os.path.exists(temp_path):
        max_attempts: int = 5
        for attempt in range(max_attempts):
            try:
                Path(temp_path).unlink()
                LOG.info(f"Temporary file {temp_path} deleted successfully")
                break
            except PermissionError as e:
                LOG.error(f"PermissionError deleting {temp_path}: {str(e)}")
                if attempt < max_attempts - 1:
                    time.sleep(0.1)
                    continue
                LOG.error(f"Failed to delete temporary file {temp_path} after {max_attempts} attempts")
            except Exception as e:
                LOG.error(f"Error deleting temporary file {temp_path}: {str(e)}")
                break


def store_bible_nodes_in_document_db(processed_bible_nodes: List[TextNode], version: str):
    """Store processed Bible nodes in a document database."""
    LOG.info(f"Storing {len(processed_bible_nodes)} processed Bible nodes for version: {version}")
    db: database.Database = get_bible_rag_db()
    bible_collection: collection.Collection = db[version]

    # Clear existing nodes for the version
    LOG.info(f"Clearing existing nodes for Bible version: {version}")
    bible_collection.delete_many({"metadata.version": version})
    LOG.info(f"Older nodes cleared from collection: {version}")

    for node in processed_bible_nodes:
        bible_collection.insert_one({
            "node_id": node.node_id,
            "text": node.get_content(),
            "metadata": node.metadata,
            "embedding": node.get_embedding()
        })

    LOG.info(f"Stored {len(processed_bible_nodes)} processed Bible nodes for version: {version}")


def tag_raw_document_with_metadata(raw_bible_page: RawDocument, prev_book: str = None, prev_chapter: int = None):
    """Tag a raw bible page with metadata."""
    bible_page_metadata: BibleMetadata = BibleMetadata()
    bible_page_match = re.search(r'(\d+)\s+([A-Za-z\s]+)\s+(\d+)$', raw_bible_page.doc_data.strip())
    
    # Extracting Bible page number, book, and chapter from the text
    if bible_page_match:
        bible_page_metadata.bible_page_number = int(bible_page_match.group(1))
        bible_page_metadata.book = bible_page_match.group(2).strip()
        bible_page_metadata.chapter = int(bible_page_match.group(3))
    else:
        bible_page_metadata.book = prev_book
        bible_page_metadata.chapter = prev_chapter

    # Extracting chapter start if present (e.g., "Chapter 1")
    chapter_match = re.search(r'Chapter\s+(\d+)', raw_bible_page.doc_data.strip())
    if chapter_match:
        bible_page_metadata.chapter = int(chapter_match.group(1))

    # Extracting verses in a page
    verse_numbers = re.findall(r'(\d+)[A-Za-z\s]', raw_bible_page.doc_data.strip())
    verse_numbers = [int(v) for v in verse_numbers]
    if verse_numbers:
        # Dropping the last verse number as it may be the bible page number
        bible_page_metadata.verses = verse_numbers[:-1]
    else:
        bible_page_metadata.verses = []

    bible_page_metadata.version = BIBLE_VERSION
    bible_page_metadata.pdf_page_number = raw_bible_page.doc_id

    raw_bible_page.metadata = bible_page_metadata.__dict__

    LOG.debug(f"Tagged metadata for page {bible_page_metadata.pdf_page_number} SUCCESSFULLY")