import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMInterface:
    """
    Interfaces with Claude to answer compliance questions.
    """

    def __init__(self, vector_store):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            print("WARNING: ANTHROPIC_API_KEY not found in environment variables")
            self.api_available = False
        else:
            self.api_available = True

        # Using the most capable model available to your account
        self.model = "claude-3-5-sonnet-20241022"  # You can change this to claude-3-7-sonnet-20250219
        self.vector_store = vector_store

    def answer_question(self, question):
        """Answer a question using relevant documents"""
        try:
            # Get relevant documents
            relevant_docs = self.vector_store.similarity_search(question, k=5)
            if not relevant_docs:
                return {
                    "answer": "I don't have enough information to answer that question. Please try asking something about Swiss banking regulations or compliance procedures.",
                    "sources": []
                }

            # Prepare context from documents with source information
            context_parts = []
            for i, doc in enumerate(relevant_docs):
                # Extract source filename from path
                source = doc.metadata.get("source", f"Document {i + 1}")
                if isinstance(source, str) and "/" in source:
                    source = os.path.basename(source)

                # Include document content with source reference
                context_parts.append(f"Source: {source}\n\n{doc.page_content}")

            context = "\n\n" + "\n\n---\n\n".join(context_parts)

            # Create a more sophisticated prompt
            prompt = self._create_prompt(question, context)

            # Query Claude API directly
            if self.api_available:
                answer = self._query_claude_api(prompt)
            else:
                answer = "API is not available. Please check your API key configuration."

            # Extract sources from the retrieved documents
            sources = [doc.metadata.get("source", "Unknown") for doc in relevant_docs]
            sources = [os.path.basename(s) if isinstance(s, str) and "/" in s else s for s in sources]

            return {
                "answer": answer,
                "sources": list(set(sources))  # Remove duplicates
            }
        except Exception as e:
            print(f"Error in answer_question: {e}")
            return {
                "answer": f"I encountered an error while processing your question: {str(e)}",
                "sources": []
            }

    def _create_prompt(self, question, context):
        """Create a well-structured prompt for compliance questions"""
        return f"""You are Claude, an AI assistant specializing in Swiss banking compliance regulations. Your primary role is to help compliance officers understand and apply the complex regulations in the Swiss banking sector.

CONTEXT INFORMATION:
{context}

GUIDELINES:
1. Base your answer SOLELY on the information provided in the context above.
2. If the context doesn't contain enough information to answer the question fully, acknowledge the limitations and suggest what additional resources might be helpful.
3. Cite specific sources (e.g., "According to the AMLA guidelines..." or "As stated in the CDB 20...").
4. Be precise about regulatory requirements, avoiding vague or general statements.
5. If appropriate, structure your answer with clear sections to improve readability.
6. Focus on practical application of regulations, not just theoretical understanding.
7. Do not reference any information outside of the provided context.

USER QUESTION:
{question}"""

    def _query_claude_api(self, prompt):
        """Query Claude API using direct HTTP request"""
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        data = {
            "model": self.model,
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()  # Raise exception for HTTP errors

            result = response.json()
            return result.get("content", [{}])[0].get("text", "No response from API")
        except Exception as e:
            print(f"API request error: {e}")
            return f"Error: Could not get a response from Claude API. {str(e)}"