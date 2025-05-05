import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMInterface:
    """
    Mock interface for compliance assistant.
    """

    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.retriever = vector_store
        print("Initialized Mock LLM Interface")

    def answer_question(self, question):
        """Answer a question using relevant documents"""
        try:
            # Get relevant documents
            relevant_docs = self.retriever.similarity_search(question)
            if not relevant_docs:
                return {
                    "answer": "I don't have enough information to answer that question. Please try asking something about Swiss banking regulations or compliance procedures.",
                    "sources": []
                }

            # Extract key information from the documents
            sources = [doc.metadata.get("source", "Unknown") for doc in relevant_docs]
            doc_texts = [doc.page_content for doc in relevant_docs]

            # Generate a mock response based on the retrieved documents
            answer = self._generate_mock_response(question, doc_texts)

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

    def _generate_mock_response(self, question, doc_texts):
        """Generate a realistic mock response based on retrieved documents"""
        # Extract key phrases and terms from the documents
        key_terms = []
        articles = []
        for text in doc_texts:
            lines = text.split('\n')
            for line in lines:
                if 'Article' in line:
                    article_match = line.strip()
                    if article_match and len(article_match) < 100:  # Avoid too long matches
                        articles.append(article_match)
                if 'AMLA' in line or 'CDB' in line or 'SOP' in line:
                    key_terms.append(line.strip())

        # Limit to unique items
        articles = list(set(articles))[:2]
        key_terms = list(set(key_terms))[:3]

        # Prepare document excerpts
        excerpts = []
        for text in doc_texts:
            sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
            for sentence in sentences[:2]:  # Take first two sentences
                if len(sentence) < 150:  # Not too long
                    excerpts.append(sentence)

        excerpts = list(set(excerpts))[:3]  # Limit to 3 unique excerpts

        # Create a response based on the question type
        question_lower = question.lower()

        if 'what' in question_lower:
            response = f"Based on the Swiss banking regulations I've analyzed, {excerpts[0] if excerpts else 'compliance officers must follow specific procedures'}. "
            if articles:
                response += f"Specifically, {articles[0]} addresses this by requiring thorough documentation and verification. "
            response += f"It's important to note that {key_terms[0] if key_terms else 'Swiss banking regulations'} emphasizes a risk-based approach to compliance."

        elif 'how' in question_lower:
            response = f"To address this properly, compliance officers should follow the procedures outlined in {articles[0] if articles else 'the relevant regulations'}. "
            if excerpts:
                response += f"This involves {excerpts[0]}. "
            response += f"Make sure to document all steps taken as required by {key_terms[0] if key_terms else 'Swiss banking regulations'}."

        elif 'when' in question_lower:
            response = f"According to {articles[0] if articles else 'Swiss banking regulations'}, the timing for this action is clearly specified. "
            if excerpts:
                response += f"{excerpts[0]}. "
            response += f"Always refer to the latest version of {key_terms[0] if key_terms else 'the compliance manual'} for the most current requirements."

        else:
            response = f"Based on the compliance documentation, {excerpts[0] if excerpts else 'financial intermediaries must follow specific guidelines'}. "
            if articles:
                response += f"{articles[0]} is particularly relevant to your question. "
            if len(excerpts) > 1:
                response += f"Furthermore, {excerpts[1]}."

        return response

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
            print(f"Sending request to Claude API with model: {self.model}")
            print(f"Prompt length: {len(prompt)} characters")

            response = requests.post(url, headers=headers, json=data)
            print(f"API response status code: {response.status_code}")

            if response.status_code != 200:
                print(f"API Error: {response.text}")
                return f"Error: API returned status code {response.status_code}"

            result = response.json()
            print("Got response from API")

            # Check if the response has the expected format
            if "content" in result and len(result["content"]) > 0:
                # Extract the response text
                response_text = result["content"][0]["text"]
                return response_text
            else:
                print(f"Unexpected response format: {result}")
                return "Error: Unexpected response format from API"

        except Exception as e:
            print(f"API request error: {e}")
            return f"Error: Could not get a response from Claude API. {str(e)}"

def _create_prompt(self, question, context):
    """Create a well-structured prompt for compliance questions"""
    return f"""You are Claude, an AI assistant specializing in Swiss banking compliance regulations. Your primary role is to help compliance officers understand and apply the complex regulations in the Swiss banking sector.

CONTEXT INFORMATION:
{context}

# Enhanced prompt for structured responses with clear markdown
You are an AI assistant specializing in Swiss banking compliance regulations.
QUESTION: {question}

FORMAT YOUR RESPONSE with these exact markdown conventions:
1. Use "## " for main section headers (with a space after ##)
2. Use "### " for subsection headers (with a space after ###)
3. Use "* " for first-level bullet points (with a space after *)
4. Avoid unnecessary nesting of bullet points. Only use "  * " for second-level bullet points when absolutely required.
5. Use "**bold text**" for important terms or article references
6. Start with a brief overview, then use sections with clear headers

Follow this markdown structure exactly to ensure proper formatting in the display interface.

GUIDELINES:
1. Base your answer SOLELY on the information provided in the context above.
2. If the context doesn't contain enough information to answer the question fully, acknowledge the limitations.

FORMAT YOUR ANSWER LIKE THIS:
- Start with a clear, direct answer to the question in 1-2 sentences
- Then organize information using clear section headers (e.g., "## Documentation Requirements")
- Use bullet points for listing requirements, procedures, or steps
- Avoid unnecessary nesting of bullet points
- Bold important terms and regulatory references using **bold** markdown
- Always include specific article references when available
- Be precise and detailed but focused on what's most relevant to the question

USER QUESTION:
{question}"""
