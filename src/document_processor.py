from langchain.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os


class DocumentProcessor:
    """
    Processes documents for the compliance assistant knowledge base.
    """

    def __init__(self, data_dir="./data"):
        self.data_dir = data_dir
        # Ensure the data directory exists
        if not os.path.exists(self.data_dir):
            print(f"Data directory {self.data_dir} does not exist. Creating it...")
            os.makedirs(self.data_dir)

    def load_documents(self):
        """Load documents from the data directory"""
        try:
            # Check if there are any text files in the directory
            text_files = [f for f in os.listdir(self.data_dir) if f.endswith('.txt')]
            if not text_files:
                print(f"No text files found in {self.data_dir}")
                return []

            print(f"Found text files: {text_files}")
            loader = DirectoryLoader(self.data_dir, glob="**/*.txt", loader_cls=TextLoader)
            documents = loader.load()
            print(f"Loaded {len(documents)} documents")
            return documents
        except Exception as e:
            print(f"Error loading documents: {e}")
            return []

    def split_documents(self, documents, chunk_size=1000, chunk_overlap=200):
        """Split documents into chunks for processing"""
        if not documents:
            print("No documents to split")
            return []

        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=["\n\n", "\n", ".", " ", ""]
            )
            chunks = text_splitter.split_documents(documents)
            print(f"Split into {len(chunks)} chunks")
            return chunks
        except Exception as e:
            print(f"Error splitting documents: {e}")
            return []