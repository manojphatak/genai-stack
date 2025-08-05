# REST API Examples for GenAI Stack

Here are practical REST API examples you can use in Postman to simulate the front-end chat interface:

## 1. Basic Chat Query (RAG Enabled)

**GET Request:**
```
http://localhost:8504/query?text=How do I create a node in Neo4j using Cypher?&rag=true
```

**Postman Setup:**
- Method: `GET`
- URL: `http://localhost:8504/query`
- Params:
  - `text`: `How do I create a node in Neo4j using Cypher?`
  - `rag`: `true`

## 2. LLM Only Query (RAG Disabled)

**GET Request:**
```
http://localhost:8504/query?text=What is the difference between Python lists and tuples?&rag=false
```

**Postman Setup:**
- Method: `GET`
- URL: `http://localhost:8504/query`
- Params:
  - `text`: `What is the difference between Python lists and tuples?`
  - `rag`: `false`

## 3. Streaming Response (Real-time like chat)

**GET Request:**
```
http://localhost:8504/query-stream?text=Explain LangChain and how it works with vector databases&rag=true
```

**Postman Setup:**
- Method: `GET`
- URL: `http://localhost:8504/query-stream`
- Params:
  - `text`: `Explain LangChain and how it works with vector databases`
  - `rag`: `true`

*Note: In Postman, you'll see the streaming response as Server-Sent Events*

## 4. Generate Support Ticket

**GET Request:**
```
http://localhost:8504/generate-ticket?text=I'm having trouble connecting to my Neo4j database from Python
```

**Postman Setup:**
- Method: `GET`
- URL: `http://localhost:8504/generate-ticket`
- Params:
  - `text`: `I'm having trouble connecting to my Neo4j database from Python`

## Quick Test Sequence

Try these in order to simulate a typical chat session:

1. **Initial Question** (with RAG):
   ```
   GET http://localhost:8504/query?text=How do I install LangChain?&rag=true
   ```

2. **Follow-up Question** (LLM only):
   ```
   GET http://localhost:8504/query?text=What are the main components of LangChain?&rag=false
   ```

3. **Generate Ticket** (if you need support):
   ```
   GET http://localhost:8504/generate-ticket?text=I need help setting up vector embeddings
   ```

## Expected Response Format

**Query Response:**
```json
{
  "result": "To create a node in Neo4j using Cypher, you can use the CREATE clause...",
  "model": "llama2"
}
```

**Ticket Response:**
```json
{
  "title": "Vector Embeddings Setup Issue",
  "description": "User needs assistance with setting up vector embeddings..."
}
```

## cURL Examples

For command line testing:

```bash
# Basic query with RAG
curl "http://localhost:8504/query?text=Hello&rag=false"

# Query with RAG enabled
curl "http://localhost:8504/query?text=How%20to%20create%20a%20Neo4j%20node&rag=true"

# Generate ticket
curl "http://localhost:8504/generate-ticket?text=Need%20help%20with%20Python"
```

Start with the basic query examples to test your setup, then try the streaming endpoint to see real-time responses like the chat interface provides!
