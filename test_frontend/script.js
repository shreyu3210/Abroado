const API_BASE_URL = 'http://localhost:8000'; // Make sure your FastAPI server is running on this port

const endpoints = {
    root: '/',
    about: '/about',
    test: '/api/test'
};

const outputElement = document.getElementById('response-output');
const loaderElement = document.getElementById('loader');

async function testEndpoint(path) {
    // Show loader, hide previous content
    loaderElement.classList.remove('hidden');
    outputElement.style.opacity = '0.5';

    try {
        const response = await fetch(`${API_BASE_URL}${path}`);

        const contentType = response.headers.get('content-type');
        let data;

        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            data = await response.text();
        }

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}\nResponse: ${JSON.stringify(data, null, 2)}`);
        }

        // Format JSON nicely if it's an object
        if (typeof data === 'object') {
            outputElement.textContent = JSON.stringify(data, null, 4);
        } else {
            outputElement.textContent = data;
        }

        outputElement.style.color = '#10b981'; // Green for success

    } catch (error) {
        outputElement.textContent = `Error fetching data:\n${error.message}`;
        outputElement.style.color = '#ef4444'; // Red for error
    } finally {
        // Hide loader, restore opacity
        loaderElement.classList.add('hidden');
        outputElement.style.opacity = '1';
    }
}

// Event Listeners for API Testing
document.getElementById('btn-root').addEventListener('click', () => testEndpoint(endpoints.root));
document.getElementById('btn-about').addEventListener('click', () => testEndpoint(endpoints.about));
document.getElementById('btn-test').addEventListener('click', () => testEndpoint(endpoints.test));


// --- CHAT INTERFACE LOGIC ---
const chatMessages = document.getElementById('chat-messages');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const btnSend = document.getElementById('btn-send');

let conversationHistory = [];

function appendMessage(sender, text) {
    const messageEl = document.createElement('div');
    messageEl.classList.add('message', `${sender}-message`);
    messageEl.textContent = text;
    chatMessages.appendChild(messageEl);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return messageEl;
}

function showTypingIndicator() {
    const indicatorEl = document.createElement('div');
    indicatorEl.classList.add('message', 'bot-message', 'typing-indicator-container');
    indicatorEl.innerHTML = `
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    chatMessages.appendChild(indicatorEl);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return indicatorEl;
}

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const userText = chatInput.value.trim();
    if (!userText) return;

    // Display user message
    appendMessage('user', userText);
    chatInput.value = '';

    // Add to conversation history
    conversationHistory.push({ role: 'user', content: userText });

    // Show typing indicator
    const typingIndicator = showTypingIndicator();

    try {
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                messages: conversationHistory
            })
        });

        // Remove typing indicator
        typingIndicator.remove();

        const data = await response.json();

        if (!response.ok) {
            const errorMessage = data.detail || 'Failed to get response from server';
            throw new Error(errorMessage);
        }

        // Extract assistant response from OpenRouter schema
        const botResponse = data.choices[0].message.content;

        // Display assistant message
        appendMessage('bot', botResponse);

        // Add to conversation history
        conversationHistory.push({ role: 'assistant', content: botResponse });

    } catch (error) {
        typingIndicator.remove();
        console.error('Chat Error:', error);
        appendMessage('error', `Error: ${error.message}`);
    }
});
