from flask import Flask, request, jsonify, render_template_string
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enhanced HTML template with better styling and structure
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Swiss Banking Compliance Assistant</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            max-width: 900px; 
            margin: 0 auto; 
            padding: 20px;
            background-color: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            color: #003366;
            border-bottom: 2px solid #003366;
            padding-bottom: 15px;
        }
        .chat-container { 
            border: 1px solid #ddd; 
            border-radius: 10px; 
            padding: 20px; 
            height: 500px; 
            overflow-y: auto; 
            margin-bottom: 20px; 
            background-color: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .user-message { 
            background-color: #e6f2ff; 
            padding: 12px 15px; 
            border-radius: 18px 18px 18px 0; 
            margin-bottom: 15px; 
            max-width: 80%;
            align-self: flex-start;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        .assistant-message { 
            background-color: #f0f7f0; 
            padding: 12px 15px; 
            border-radius: 18px 18px 0 18px; 
            margin-bottom: 15px; 
            max-width: 80%;
            margin-left: auto;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        .assistant-message h3 {
            margin-top: 10px;
            margin-bottom: 5px;
            color: #003366;
            font-size: 16px;
        }
        .assistant-message ul {
            margin: 5px 0;
            padding-left: 20px;
        }
        .assistant-message li {
            margin-bottom: 5px;
        }
        .assistant-message strong {
            color: #004080;
            font-weight: bold;
        }
        .sources { 
            font-size: 0.8em; 
            color: #666; 
            margin-top: 8px; 
            border-top: 1px solid #eee;
            padding-top: 8px;
        }
        .input-container {
            display: flex;
            gap: 10px;
        }
        input[type="text"] { 
            flex: 1;
            padding: 12px; 
            border: 1px solid #ddd; 
            border-radius: 25px; 
            font-size: 16px;
            outline: none;
        }
        input[type="text"]:focus {
            border-color: #003366;
            box-shadow: 0 0 5px rgba(0,51,102,0.3);
        }
        button { 
            padding: 12px 25px; 
            background-color: #003366; 
            color: white; 
            border: none; 
            border-radius: 25px; 
            cursor: pointer; 
            font-weight: bold;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #004c99;
        }
        .example-questions {
            margin-top: 30px;
            background-color: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .example-questions h3 {
            margin-top: 0;
            color: #003366;
        }
        .example-question {
            display: inline-block;
            margin: 5px;
            padding: 8px 15px;
            background-color: #e6f2ff;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            transition: background-color 0.2s;
        }
        .example-question:hover {
            background-color: #cce5ff;
        }
        .loading {
            text-align: center;
            padding: 20px;
            display: none;
        }
        .loading:after {
            content: "⏳";
            animation: loading 1.5s infinite;
            display: inline-block;
        }
        @keyframes loading {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Swiss Banking Compliance Assistant</h1>
        <p>Ask questions about Swiss banking regulations and compliance procedures</p>
    </div>

    <div class="chat-container" id="chat-container">
        <div class="assistant-message">Welcome! I'm your Swiss banking compliance assistant powered by Claude. How can I help you understand Swiss banking regulations today?</div>
    </div>

    <div class="loading" id="loading">Processing your question...</div>

    <div class="input-container">
        <input type="text" id="user-input" placeholder="Ask a question about Swiss banking compliance...">
        <button id="send-button">Send</button>
    </div>

    <div class="example-questions">
        <h3>Example Questions</h3>
        <div class="example-question" id="example1">What documentation is required for identifying natural persons?</div>
        <div class="example-question" id="example2">When is enhanced due diligence required?</div>
        <div class="example-question" id="example3">How should banks handle beneficial owners of domiciliary companies?</div>
        <div class="example-question" id="example4">What are the requirements for PEP monitoring?</div>
        <div class="example-question" id="example5">What are the reporting obligations for suspicious transactions?</div>
    </div>

    <script>
        // Example questions functionality
        document.querySelectorAll('.example-question').forEach(function(element) {
            element.addEventListener('click', function() {
                document.getElementById('user-input').value = this.textContent;
            });
        });

        // Send message functionality
        document.getElementById('send-button').addEventListener('click', function() {
            sendMessage();
        });

        document.getElementById('user-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        function sendMessage() {
            const userInput = document.getElementById('user-input');
            const chatContainer = document.getElementById('chat-container');
            const loadingIndicator = document.getElementById('loading');

            if (userInput.value.trim() === '') return;

            // Add user message
            const userMessage = document.createElement('div');
            userMessage.className = 'user-message';
            userMessage.textContent = userInput.value;
            chatContainer.appendChild(userMessage);

            // Show loading indicator
            loadingIndicator.style.display = 'block';

            // Scroll to bottom
            chatContainer.scrollTop = chatContainer.scrollHeight;

            // Send to backend
            fetch('/query', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query: userInput.value})
            })
            .then(function(response) {
                return response.json();
            })
            .then(function(data) {
                // Hide loading indicator
                loadingIndicator.style.display = 'none';

                // Create assistant message
                const assistantMessage = document.createElement('div');
                assistantMessage.className = 'assistant-message';

                // Process the answer text - handle simple formatting
                let formattedAnswer = data.answer;

                // Format the text with some basic HTML
                formattedAnswer = formattedAnswer
                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // Bold
                    .replace(/## (.*?)\\n/g, '<h3>$1</h3>')            // Headers
                    .replace(/- (.*?)\\n/g, '<li>$1</li>')             // List items
                    .replace(/<li>/g, '<ul><li>').replace(/<\/li>\\n/g, '</li></ul>') // Wrap list items
                    .replace(/\\n\\n/g, '<br><br>')                    // Paragraphs
                    .replace(/\\n/g, '<br>');                         // Line breaks

                assistantMessage.innerHTML = formattedAnswer;

                // Add sources if available
                if (data.sources && data.sources.length > 0) {
                    const sources = document.createElement('div');
                    sources.className = 'sources';
                    sources.textContent = 'Sources: ' + data.sources.join(', ');
                    assistantMessage.appendChild(sources);
                }

                chatContainer.appendChild(assistantMessage);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            })
            .catch(function(error) {
                // Hide loading indicator
                loadingIndicator.style.display = 'none';

                console.error('Error:', error);

                // Add error message
                const errorMessage = document.createElement('div');
                errorMessage.className = 'assistant-message';
                errorMessage.textContent = 'Sorry, there was an error processing your request: ' + error.message;
                chatContainer.appendChild(errorMessage);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            });

            userInput.value = '';
        }
    </script>
</body>
</html>
'''


# Improved prompt for better structured responses
def query_claude_api(question):
    """Query Claude API with a structured prompt"""
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        return "API key not found. Please check your .env file."

    # Enhanced prompt for structured responses
    prompt = f"""You are an AI assistant specializing in Swiss banking compliance regulations. Your primary role is to help compliance officers understand and apply complex regulations in the Swiss banking sector.

QUESTION: {question}

Please provide a structured response that:
1. Starts with a direct, concise answer (1-2 sentences)
2. Uses section headers (## Section Title) for different aspects of the answer
3. Uses bullet points (- point) for listing requirements or steps
4. Bolds (**important terms**) key regulatory terms or article references
5. Cites specific regulations when possible (e.g., "According to AMLA Article 3...")
6. Focuses on practical application and implementation

FORMAT YOUR ANSWER using the formatting instructions above to make it easy to scan and understand."""

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    data = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 800,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        print("Sending request to Claude API...")
        response = requests.post(url, headers=headers, json=data)
        print(f"Response status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if "content" in result and len(result["content"]) > 0:
                return result["content"][0]["text"]
            else:
                print(f"Unusual response format: {result}")
                return "Error: Unexpected response format"
        else:
            print(f"API error: {response.text}")
            return f"Error {response.status_code}: {response.text}"

    except Exception as e:
        print(f"Exception: {e}")
        return f"Error: {str(e)}"


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/query', methods=['POST'])
def query():
    data = request.json
    question = data.get('query', '')

    print(f"Received question: {question}")

    if not question:
        return jsonify({"error": "No question provided"}), 400

    # Get answer from Claude
    answer = query_claude_api(question)
    print(f"Generated answer (first 100 chars): {answer[:100]}...")

    # For now, use static example sources
    # In your real app, you would get these from your vector store
    sources = ["Swiss Banking Act", "AMLA Guidelines", "CDB 20 Regulations"]

    return jsonify({
        "answer": answer,
        "sources": sources
    })


if __name__ == '__main__':
    print("Starting enhanced compliance assistant on http://127.0.0.1:5000")
    app.run(debug=True, port=5001)