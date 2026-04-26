# Bhoomi RAG API

Simple FastAPI backend for the existing RAG project.

## Endpoints

- `GET /` - health check
- `GET /ask?query=...` - secured RAG answer endpoint

## Local Setup

```bash
pip install -r requirements.txt
python src/generate_api_key.py
```

Create `.env` and set:

```env
API_KEY=your_generated_api_key
GROQ_API_KEY=your_groq_api_key
GOOGLE_DRIVE_FOLDER_URL=https://drive.google.com/drive/folders/your_folder_id
PDF_DATA_DIR=data/pdfs
CHROMA_DB_PATH=chroma_data
RAG_COLLECTION_NAME=rice_crops
```

Run the API:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 10000
```

## First Run Behavior

If `CHROMA_DB_PATH` already contains data, the API uses it directly.

If no ChromaDB data exists, the API downloads PDFs from Google Drive, processes them, creates embeddings, and stores them in ChromaDB.

## Render Deployment

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 10000
```

Set these environment variables in Render:

```env
API_KEY=your_secure_api_key
GROQ_API_KEY=your_groq_api_key
GOOGLE_DRIVE_FOLDER_URL=https://drive.google.com/drive/folders/your_folder_id
PDF_DATA_DIR=data/pdfs
CHROMA_DB_PATH=chroma_data
RAG_COLLECTION_NAME=rice_crops
```

## Example Request

```bash
curl -X GET "https://your-render-app.onrender.com/ask?query=What%20is%20rice%20blast%20disease%3F" \
  -H "x-api-key: your_secure_api_key"
```

Frontend example:

```javascript
const response = await fetch(
  "https://your-render-app.onrender.com/ask?query=What%20is%20rice%20blast%20disease%3F",
  {
    headers: {
      "x-api-key": import.meta.env.VITE_BHOOMI_API_KEY,
    },
  }
);

const data = await response.json();
console.log(data.answer);
```
