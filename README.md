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
    "data": "The Bible speaks extensively on the topic of forgiveness, emphasizing its importance in several passages. In Matthew 18:21-22, Peter asks Jesus how often he should forgive his brother, to which Jesus responds, \"I say not unto thee, Until seven times: but, Until seventy times seven.\" This teaching underscores the boundless nature of forgiveness expected from believers.\n\nAdditionally, Jesus illustrates forgiveness through a parable later in the same chapter (Matthew 18:23-35), where a king forgives a servant's immense debt, yet that servant refuses to forgive a fellow servant a much smaller debt. This parable concludes with a sobering reminder from Jesus: \"So likewise shall my heavenly Father do also unto you, if ye from your hearts forgive not every one his brother their trespasses\" (Matthew 18:35).\n\nFurthermore, during the Sermon on the Mount, Jesus instructs believers on the importance of reconciliation and forgiveness. He says, \"If thou bring thy gift to the altar, and there rememberest that thy brother hath ought against thee; Leave there thy gift before the altar, and go thy way; first be reconciled to thy brother, and then come and offer thy gift\" (Matthew 5:23-24). This emphasizes that reconciliation with others is crucial and takes precedence even over offering gifts to God.\n\nThese passages reflect the centrality of forgiveness in Christian teachings, portraying it as an essential quality for followers of Christ.",
    "message": "RAG query processed",
    "session_id": "2ace4b43-d332-4818-8732-35faf8e5d93d",
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