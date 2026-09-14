from fastapi import FastAPI
from pydantic import BaseModel
import chromadb

app = FastAPI(
    title="BioAsistan API",
    description="Akıllı Biyokimya ve Araştırma Asistanı Arka Plan Servisi",
    version="0.2.0"
)

# not: ChromaDB Vektör Veritabanı İstemcisi (Veriler 'bio_memory' klasöründe saklanır)
chroma_client = chromadb.PersistentClient(path="./bio_memory")
collection = chroma_client.get_or_create_collection(name="biochemistry_docs")


class DocumentInput(BaseModel):
    doc_id: str
    content: str
    source: str


class QueryRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {
        "system": "BioAsistan",
        "status": "Online",
        "memory_status": "ChromaDB Connected"
    }


# not:  Hafızaya Bilgi Ekleme Uç Noktası
@app.post("/add-knowledge")
def add_knowledge(doc: DocumentInput):
    collection.add(
        documents=[doc.content],
        ids=[doc.doc_id],
        metadatas=[{"source":doc.source}]
    )
    return {
        "status": "Success",
        "message": f"'{doc.doc_id}' kimlikli bilgi BioAsistan hafızasına eklendi."

    }


# Hafızada Anlamsal Arama Uç Noktası
@app.post("/ask")
def ask_assistant(request: QueryRequest):
    results = collection.query(
        query_texts=[request.question],
        n_results=2
    )
    retrieved_docs = results['documents'][0] if results['documents'] else []

    return {
        "system": "BioAsistan",
        "question": request.question,
        "retrieved_context": retrieved_docs,
        "status": "Relevant documents retrieved from memory."
    }