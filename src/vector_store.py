import os
import re
from langchain.schema import Document


class VectorStore:
    """
    A simplified vector store using keyword matching.
    """

    def __init__(self, index_name="compliance_assistant"):
        self.index_name = index_name
        self.documents = []
        self.vector_store = self  # For compatibility with existing code

    def create_vector_store(self, documents):
        """Store documents"""
        print(f"Creating vector store with {len(documents)} documents")
        self.documents = documents
        return self

    def load_vector_store(self):
        """Nothing to load for this simple implementation"""
        return self

    def _save_vector_store(self):
        """Nothing to save for this simple implementation"""
        pass

    def as_retriever(self, search_type=None, search_kwargs=None):
        """Return self as a retriever"""
        return self

    def similarity_search(self, query, k=4):
        """
        Simple keyword-based search
        """
        print(f"Searching for: {query}")
        if not self.documents:
            print("No documents in vector store")
            return []

        # Convert query to lowercase and split into keywords
        keywords = re.findall(r'\w+', query.lower())

        # Score documents based on keyword matches
        scored_docs = []
        for doc in self.documents:
            content = doc.page_content.lower()
            score = sum(1 for keyword in keywords if keyword in content)
            scored_docs.append((score, doc))

        # Sort by score (highest first) and take top k
        scored_docs.sort(reverse=True, key=lambda x: x[0])
        results = [doc for score, doc in scored_docs[:k] if score > 0]

        # If we don't have enough results, just return the first k documents
        if len(results) < k:
            print(f"Not enough matching documents, returning top {min(k, len(self.documents))}")
            results = self.documents[:min(k, len(self.documents))]

        print(f"Found {len(results)} relevant documents")
        return results