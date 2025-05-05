from flask import Flask, request, jsonify, render_template_string
from document_processor import DocumentProcessor
from vector_store import VectorStore
from llm_interface import LLMInterface
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize components
print("Initializing document processor...")
doc_processor = DocumentProcessor(data_dir="./data")

# Check if vector store exists, if not create it
vector_store = VectorStore()
if not os.path.exists("compliance_assistant.faiss"):
    print("Vector store not found. Creating new vector store...")
    documents = doc_processor.load_documents()
    if documents:
        chunks = doc_processor.split_documents(documents)
        if chunks:
            vector_store.create_vector_store(chunks)
        else:
            print("No chunks created. Unable to create vector store.")
    else:
        print("No documents loaded. Unable to create vector store.")
else:
    print("Loading existing vector store...")
    vector_store.load_vector_store()

# Initialize LLM interface
print("Initializing LLM interface...")
llm_interface = LLMInterface(vector_store)

# HTML template for the web interface with improved styling
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
            background-color: #f9f9f9;
            color: #333;
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
        .assistant-message h3 {
    margin-top: 15px;
    margin-bottom: 8px;
    color: #003366;
    border-bottom: 1px solid #eee;
    padding-bottom: 5px;
}

.assistant-message strong {
    font-weight: bold;
    color: #004080;
}

.assistant-message ul {
    margin: 5px 0;
    padding-left: 20px;
}

.assistant-message li {
    margin: 3px 0;
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
        .loading {
            display: none;
            margin: 10px 0;
            color: #666;
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
        }
        .example-question:hover {
            background-color: #cce5ff;
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
    
    <div class="loading" id="loading">
        <p>Processing your question...</p>
    </div>
    
    <div class="input-container">
        <input type="text" id="user-input" placeholder="Ask a question about Swiss banking compliance...">
        <button onclick="sendMessage()">Send</button>
    </div>
    
    <div class="example-questions">
        <h3>Example Questions</h3>
        <div id="example1" class="example-question">What documentation is required for identifying natural persons?</div>
        <div id="example2" class="example-question">When is enhanced due diligence required?</div>
        <div id="example3" class="example-question">How should banks handle beneficial owners of domiciliary companies?</div>
        <div id="example4" class="example-question">What are the requirements for PEP monitoring?</div>
        <div id="example5" class="example-question">What are the reporting obligations for suspicious transactions?</div>
    </div>
    
    <script>
        // Function to handle example question clicks
        document.getElementById('example1').addEventListener('click', function() {
            document.getElementById('user-input').value = this.textContent;
        });
        document.getElementById('example2').addEventListener('click', function() {
            document.getElementById('user-input').value = this.textContent;
        });
        document.getElementById('example3').addEventListener('click', function() {
            document.getElementById('user-input').value = this.textContent;
        });
        document.getElementById('example4').addEventListener('click', function() {
            document.getElementById('user-input').value = this.textContent;
        });
        document.getElementById('example5').addEventListener('click', function() {
            document.getElementById('user-input').value = this.textContent;
        });
        
        function sendMessage() {
            const userInput = document.getElementById('user-input');
            const chatContainer = document.getElementById('chat-container');
            const loadingIndicator = document.getElementById('loading');
            
            if (userInput.value.trim() === '') return;
            
            // Display user message
            const userMessage = document.createElement('div');
            userMessage.className = 'user-message';
            userMessage.textContent = userInput.value;
            chatContainer.appendChild(userMessage);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            
            // Show loading indicator
            loadingIndicator.style.display = 'block';
            
            console.log("Sending query to backend:", userInput.value);
            
            // Send query to backend
            fetch('/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: userInput.value })
            })
            .then(response => {
                console.log("Received response from server:", response);
                return response.json();
            })

.then(data => {
    console.log("Parsed JSON data:", data);
    
    // Hide loading indicator
    loadingIndicator.style.display = 'none';
    
    // Display assistant message
    const assistantMessage = document.createElement('div');
    assistantMessage.className = 'assistant-message';
    
    if (data.error) {
        assistantMessage.textContent = "Error: " + data.error;
    } else {
        // Handle markdown-style formatting
        let formattedAnswer = data.answer;
        
        // Replace section headers (##)
        formattedAnswer = formattedAnswer.replace(/## (.*?)(\n|$)/g, '<h3>$1</h3>');
        
        // Replace bold text (**text**)
        formattedAnswer = formattedAnswer.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Replace bullet points
        formattedAnswer = formattedAnswer.split('\n').map(line => {
            if (line.trim().startsWith('-')) {
                return '<li>' + line.trim().substring(1).trim() + '</li>';
            }
            return line;
        }).join('\n');
        formattedAnswer = formattedAnswer.replace(/<li>/g, '<ul><li>').replace(/<\/li>\n/g, '</li></ul>\n');
        
        // Handle paragraphs
        formattedAnswer = formattedAnswer.replace(/\n\n/g, '<br><br>').replace(/\n/g, '<br>');
        
        assistantMessage.innerHTML = formattedAnswer;
        
        // Add sources if available
        if (data.sources && data.sources.length > 0) {
            const sources = document.createElement('div');
            sources.className = 'sources';
            sources.textContent = 'Sources: ' + data.sources.join(', ');
            assistantMessage.appendChild(sources);
        }
    }
    
    chatContainer.appendChild(assistantMessage);
    chatContainer.scrollTop = chatContainer.scrollHeight;
})
         .catch(error => {
                console.error('Error:', error);
                
                // Hide loading indicator
                loadingIndicator.style.display = 'none';
                
                // Handle any errors
                const errorMessage = document.createElement('div');
                errorMessage.className = 'assistant-message';
                errorMessage.textContent = "Sorry, there was an error processing your request: " + error.message;
                chatContainer.appendChild(errorMessage);
            });
            
            userInput.value = '';
        }
        
        // Allow sending message with Enter key
        document.getElementById('user-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
'''


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/query', methods=['POST'])
def query():
    data = request.json
    query = data.get('query', '')

    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        result = llm_interface.answer_question(query)
        return jsonify(result)
    except Exception as e:
        print(f"Error processing query: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/feedback', methods=['POST'])
def feedback():
    """Collect feedback for continuous improvement"""
    data = request.json
    query = data.get('query', '')
    answer = data.get('answer', '')
    rating = data.get('rating', 0)
    comments = data.get('comments', '')

    # Store feedback for future model improvements
    # This could write to a database or log file
    print(f"Feedback received - Rating: {rating}/5")
    print(f"Query: {query}")
    print(f"Answer: {answer}")
    print(f"Comments: {comments}")

    return jsonify({"status": "Feedback received"}), 200


if __name__ == '__main__':
    app.run(debug=True)


    @app.route('/query', methods=['POST'])
    def query():
        data = request.json
        query = data.get('query', '')

        print(f"Received query: {query}")

        if not query:
            print("Error: No query provided")
            return jsonify({"error": "No query provided"}), 400

        try:
            print("Calling LLM interface...")
            result = llm_interface.answer_question(query)
            print(f"Result: {result}")
            return jsonify(result)
        except Exception as e:
            print(f"Error processing query: {e}")
            return jsonify({"error": str(e)}), 500