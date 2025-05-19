from pathlib import Path
import json
from langchain.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.docstore.document import Document

DATA_FILE = Path("data/artikel_budaya_bali_inggris.json")
CHROMA_DIR = Path("load_data/chroma_db")
CHROMA_COLLECTION_FILE = CHROMA_DIR / "chroma-collections.parquet"

def load_json_data(filepath: Path) -> list[dict]:
    with filepath.open("r", encoding="utf-8") as file:
        return json.load(file)

def prepare_documents(data: list[dict]) -> list[Document]:
    return [
        Document(
            page_content=item["Isi Lengkap"],
            metadata={
                "title": item["Judul"],
                "url": item["Link Artikel"]
            }
        )
        for item in data
    ]

def load_and_persist_chroma(documents: list[Document], persist_dir: Path):
    embedding = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = Chroma.from_documents(
        documents,
        embedding=embedding,
        persist_directory=str(persist_dir)
    )
    vectordb.persist()
    print("Data has been successfully loaded and saved to ChromaDB.")

# execution block

if CHROMA_COLLECTION_FILE.exists():
    print("ChromaDB already exists. Reloading is not necessary.")
else:
    if not DATA_FILE.exists():
        print(f"Data file not found: {DATA_FILE}")
    else:
        print("Loading data from JSON and saving to ChromaDB...")
        data = load_json_data(DATA_FILE)
        documents = prepare_documents(data)
        load_and_persist_chroma(documents, CHROMA_DIR)
