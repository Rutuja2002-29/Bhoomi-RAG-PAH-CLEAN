module.exports = {
  apps: [
    {
      name: "bhoomi-rag-api",
      script: "uvicorn",
      args: "main:app --host 0.0.0.0 --port 8000",
      cwd: "./src",
      interpreter: "none",
      env: {
        GROQ_API_KEY: "your_groq_api_key_here"
      }
    }
  ]
};