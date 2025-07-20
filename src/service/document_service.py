import logging
import tempfile
import pymupdf
import os
import time
from typing import Dict, List
from werkzeug.datastructures import FileStorage
from pathlib import Path
from pymupdf import Document as pypdfDocument, Page as pypdfPage
from src.models import RawDocument, BibleRequest, BibleResponse, BibleReference

LOG = logging.getLogger(__name__)
extensions: List[str] = ['.pdf']

def process_documents(bible_request: BibleRequest):
    """Process the documents in the BibleRequest."""
    file_names: List[str] = [file.filename for file in bible_request.files]
    total_files: int = len(file_names)
    LOG.info(f"document_service: Processing {total_files} files STARTED: {file_names}")

    for file in bible_request.files:
        extracted_bible_data: List[RawDocument] = extract_file(file=file)
        LOG.info(f"document_service: Extracted {len(extracted_bible_data)} pages from {file.filename}")
    
        LOG.info(f"document_service: Processing COMPLETED for {file.filename}")




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
                for page_number in range(bible_document.page_count):
                    pdf_page: pypdfPage = bible_document.load_page(page_number)
                    text: str = pdf_page.get_text("text").replace('\n', ' ')
                    raw_page: RawDocument = RawDocument(doc_id=page_number, doc_data=text)
                    raw_bible.append(raw_page)

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
                LOG.debug(f"Temporary file {temp_path} deleted successfully")
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


def store_bible_nodes_in_document_db(processed_bible_nodes: List[RawDocument], version: str):
    """Store processed Bible nodes in a document database."""
    LOG.info(f"Storing {len(processed_bible_nodes)} processed Bible nodes for version: {version}")