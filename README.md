# Secure RAG Application for Banking

This project demonstrates a Secure Retrieval-Augmented Generation (RAG) system tailored for the banking sector. It enforces rigorous data handling controls—specifically content sanitization and pseudonymization—before any sensitive data enters the vector database or LLM context window.

## 🔐 Security Layers in the Backend

1. **Threat Detection**:
   Scans incoming documents and user queries using robust heuristics and regular expressions to block SQL injection (`DROP TABLE`, `UNION SELECT`), XSS payloads (`<script>`), and command injections. Malicious input drops the document and instantly blocks the user entirely.

2. **Content Sanitization**:
   Cleanses the content by stripping out hazardous patterns or code segments while preserving the benign text context.

3. **Entity Differentiation (PII Detection)**:
   Our system parses the document content to identify Personally Identifiable Information (PII) specific to the banking domain using Regular Expressions (Regex). How it differentiates:
   - **Account Numbers**: `\b\d{9,18}\b` matches potential banking account lengths.
   - **IFSC Codes**: `[A-Z]{4}0[A-Z0-9]{6}` strictly matches the Indian Financial System Code format.
   - **Phone Numbers**: `\b\d{10}\b` standard 10-digit matching.
   - **Email Addresses**: Standard `\S+@\S+` matching.

4. **Pseudonymization**:
   Identified entities are immediately substituted with a non-reversible secure format before storage (e.g., `ACCOUNT_8f2a1b`). This prevents user data from propagating into the AI model's context window.

## 🧠 System Architecture

### Vector Database Integration (Faiss)
The application vectorizes plain text (or extracted PDF text) using the **OpenAI Embedding Model (`text-embedding-3-small`)**. These high-dimensional embeddings (1536 dimensions) are then persisted using **Faiss** (Facebook AI Similarity Search).
To ensure Role-Based Access Control (RBAC):
- The `db.py` layer maintains an isolated `faiss.IndexFlatL2` per user entity. 
- "Admins" populate the global knowledge base index. 
- "Users" populate their isolated personal index. When queried, Faiss retrieves context from both the global Admin index and the individual User's index securely.

### OpenAI LLM Integration
We query the **OpenAI `gpt-4o-mini`** model for generating answers. Crucially, the context provided to the LLM is retrieved from the safely anonymized, sanitized Faiss knowledge base.

## 🚀 Running the API & Demo Locally

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure API Key:**
   Set your `OPENAI_API_KEY` in `backend/config.py`.
3. **Run the Interactive Demo for Professors:**
   Run the simulation to understand and visually showcase the backend security layers:
   ```bash
   python backend/demo.py
   ```
4. **Start the Application:**
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

## 🌍 Production Deployment Guide

To deploy this minimal project architecture out to a real-world web application:

1. **Replace In-Memory Structures:**
   - Instead of storing users and Faiss indices in local memory, configure a persistent database like **PostgreSQL** or **MongoDB**.
   - Use a specialized, distributed vector database like **Pinecone**, **Weaviate**, or **Milvus** to replace `faiss-cpu`.
2. **Containerize the Backend (Docker):**
   Create a `Dockerfile` for your Python server:
   ```dockerfile
   FROM python:3.10-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```
3. **Containerize the Frontend (React):**
   ```dockerfile
   FROM node:18-alpine
   WORKDIR /app
   COPY package.json .
   RUN npm install
   COPY . .
   RUN npm run build
   # Example: Serve the built vite/webpack assets using Nginx
   ```
4. **Deploy using a Cloud Provider:**
   - **Render / Heroku**: The fastest way to launch the Dockerized backend and frontend without infra setup. Just connect your GitHub repo to their services.
   - **AWS Cloud**: Deploy your API backend via AWS Elastic Container Service (ECS) with Fargate. Host your frontend build on AWS S3 with CloudFront. Connect backend to managed AWS RDS database.
