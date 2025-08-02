from flask import Request, Response
from pydantic import BaseModel, Field
from typing import Any, Optional, Dict, List
from werkzeug.datastructures import FileStorage
from dataclasses import dataclass

@dataclass
class RawDocument:
    """Represents a raw document with its content and metadata."""
    doc_id: str = Field(..., description="Unique identifier for the document")
    doc_data: str = Field(..., description="Content of the document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata associated with the document")


@dataclass 
class BibleReference:
    """Represents a reference to a Bible verse or passage."""
    book: str = Field(..., description="Book of the Bible")
    chapter: int = Field(..., description="Chapter number")
    verse: Optional[int] = Field(None, description="Verse number (optional for ranges)")
    end_verse: Optional[int] = Field(None, description="End verse number (for ranges)")



@dataclass
class BibleRequest:
    """Represents a request to process Bible-related data."""
    version: str = Field(..., description="Bible version to use")
    query: Optional[str] = Field(..., description="Query string for the Bible request")
    bible_references: Optional[List[BibleReference]] = Field(None, description="List of Bible references")
    files: Optional[List[FileStorage]] = Field(None, description="List of files to be processed")
    qna: bool = Field(False, description="Flag to indicate if the request is for a Q&A process")
    session_id: Optional[str] = Field(None, description="Session ID for tracking the request")

    @classmethod
    def from_request(cls, request: Request, qna: bool) -> 'BibleRequest':
        """Create a BibleRequest instance from a Flask request."""
        if qna:
            data = request.get_json()
            return cls(
            version=data['version'],
            query=data['query'],
            bible_references=[
                BibleReference(**ref) for ref in data.get('bible_references', [])
            ],
            session_id=data['session_id'])
        else: 
            data = request.form
            return cls(
                version=data['version'],
                files=request.files.getlist('files') if 'files' in request.files else []
            )
    
@dataclass
class BibleResponse(Response):
    """Represents a response containing Bible-related data."""
    
    @staticmethod
    def success(status: str, message: str, data: Optional[object] = None, session_id: Optional[str] = None, code: int = 200) -> 'BibleResponse':
        """Create a successful response."""
        if data is not None:
            return {"status": status, "message": message, "data": data, "session_id": session_id}, code
        else:
            return {"status": status, "message": message, "session_id": session_id}, code
        
    @staticmethod
    def failure(status: str, message: str, code: int = 500) -> 'BibleResponse':
        """Create an error response."""
        return {"status": status, "message": message}, code
    
    @staticmethod
    def not_found(status: str, message: str, code: int = 404) -> 'BibleResponse':
        """Create a not foudn response."""
        return {"status": status, "message": message}, code


class BibleMetadata(BaseModel):
    book: Optional[str] = Field(None, description="Book of the Bible")
    chapter: Optional[int] = Field(None, description="Chapter number")
    verses: Optional[List[int]] = Field([], description="Verse numbers (optional for ranges)")
    version: Optional[str] = Field(None, description="Bible version")
    bible_page_number: Optional[int] = Field(None, description="Page number in the Bible document")
    pdf_page_number: Optional[int] = Field(None, description="PDF page number where the text is located")

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True)

