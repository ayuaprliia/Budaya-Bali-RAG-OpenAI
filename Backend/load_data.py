from pathlib import Path
import json
from langchain.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.docstore.document import Document

DATA_FILE = Path("data/artikel_budaya_bali_inggris.json")
CHROMA_DIR = Path("load_data/chroma_db")
MODEL_NAME = "all-MiniLM-L6-v2"

def chroma_db_exists(chroma_dir: Path) -> bool:
    return (chroma_dir / "chroma-collections.parquet").exists() and \
           (chroma_dir / "chroma-embeddings.parquet").exists()

def load_json_data(filepath: Path) -> list[dict]:
    try:
        with filepath.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading JSON: {e}")
        return []

def prepare_documents(data: list[dict]) -> list[Document]:
    documents = []
    for item in data:
        if "Isi Lengkap" in item and "Judul" in item and "Link Artikel" in item:
            documents.append(Document(
                page_content=item["Isi Lengkap"],
                metadata={
                    "title": item["Judul"],
                    "url": item["Link Artikel"],
                    "image": item.get("Link Gambar", "")
                }
            ))
    return documents

def load_and_persist_chroma(documents: list[Document], persist_dir: Path):
    embedding = SentenceTransformerEmbeddings(model_name=MODEL_NAME)
    vectordb = Chroma.from_documents(
        documents,
        embedding=embedding,
        persist_directory=str(persist_dir)
    )
    vectordb.persist()
    print("Data has been successfully loaded and saved to ChromaDB.")

if chroma_db_exists(CHROMA_DIR):
    print("ChromaDB already exists. Reloading is not necessary.")
else:
    if not DATA_FILE.exists():
        print(f"Data file not found: {DATA_FILE}")
    else:
        print("Loading data from JSON and saving to ChromaDB...")
        data = load_json_data(DATA_FILE)
        documents = prepare_documents(data)
        load_and_persist_chroma(documents, CHROMA_DIR)
