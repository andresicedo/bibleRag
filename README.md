# bibleRag

**bibleRag** is a Retrieval-Augmented Generation (RAG) application that enables intelligent question-and-answer (QnA) interactions with the King James Version (KJV) of the Holy Bible.  
The system uses modern natural language processing techniques to retrieve contextually relevant passages and generate accurate, grounded responses.

---

## Technologies Used

- **Python Flask** – REST API framework for request handling and endpoint management
- **AWS OpenSearch** – Vector store for k-Nearest Neighbor (k-NN) similarity search
- **MongoDB Atlas** – Document database for storing chunked Bible text with metadata
- **OpenAI GPT-4o (2024-08-06)** – LLM for generating QnA responses
- **OpenAI text-embedding-3-small** – Embedding model for vectorizing text chunks
- **PDF Processing Tools** – Extract and preprocess text from the KJV Bible PDF

---

## Example QnA API Request

**Endpoint:**  
`POST /kjv/query`

**Request Payload:**
```json
{
    "version": "kjv",
    "query": "What does the Bible say about forgiveness?",
    "bible_references": [
        {
            "book": "Matthew"
        }
    ],
    "session_id": "<<-- optional field. A session ID will be created if not provided. Use it to maintain chat history across multiple questions.>>"
}
```


**Response Payload:**
```json
{
    "data": "The field referenced as the \"field of blood\" is called \"Aceldama.\" This is noted in Acts 1:19: \"And it was known unto all the dwellers at Jerusalem; insomuch as that field is called in their proper tongue, Aceldama, that is to say, The field of blood.\"",
    "message": "RAG query processed",
    "session_id": "83402842-36cf-4a68-af24-31b4aba13144",
    "status": "SUCCESS"
}
```


# QnA Best Practices

To get the most accurate results when using bibleRag, follow these guidelines:

## Ask Specific Questions

The system works best when queries target a specific topic, verse, or character.

Example:
- ✅ "Who replaced Judas in the Book of Acts?"
- ❌ "Summarize the Book of Acts"

## Use Metadata Filters

Narrow searches by specifying the book (and optionally chapter) in your request. This reduces noise and improves retrieval precision.

## Phrase Questions in Modern English

While the KJV text uses older English, framing questions in modern, clear English helps the system interpret intent more effectively.

## Leverage Session IDs for Context

When continuing a conversation, provide the same session_id to maintain chat history and enable more context-aware answers.

## Avoid Overly Broad Requests

Very general or summary-style requests may return fragmented results, as RAG is optimized for targeted retrieval.