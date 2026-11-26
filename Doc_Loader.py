from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_PDF = PROJECT_DIR / "sample.pdf"


def load_and_split_pdf(pdf_path=DEFAULT_PDF, chunk_size=800, chunk_overlap=100):
    """Load a PDF and split its pages into overlapping text chunks."""
    pdf_path = Path(pdf_path).expanduser().resolve()
    if not pdf_path.is_file():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}\n"
            "Place the PDF next to Doc_Loader.py or pass its path to load_and_split_pdf()."
        )

    documents = PyPDFLoader(str(pdf_path)).load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    return splitter.split_documents(documents)


if __name__ == "__main__":
    chunks = load_and_split_pdf()
    print(f"Total chunks: {len(chunks)}")
    if chunks:
        print(chunks[0].page_content[:500])
