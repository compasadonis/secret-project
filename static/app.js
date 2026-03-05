
// Chatbot & Quiz Script
document.addEventListener('DOMContentLoaded', () => {
  // Chat elements
  const chatMessages = document.getElementById('chat-messages');
  const chatInput = document.getElementById('chat-input');
  const chatSend = document.getElementById('chat-send');

  // Function to add a message to chat
  function addMessage(text, from = 'bot') {
    if (!chatMessages) return; // safety check
    const div = document.createElement('div');
    div.className = `chat-msg ${from}`;
    div.textContent = text;
    chatMessages.appendChild(div);
    chatMessages.scrollTo({ top: chatMessages.scrollHeight, behavior: 'smooth' });
  }

  // Function to add suggestion buttons
  function addSuggestions(suggestions) {
    if (!chatMessages) return;
    const container = document.createElement('div');
    container.className = 'chat-suggestions';
    suggestions.forEach(s => {
      const btn = document.createElement('button');
      btn.className = 'suggestion-btn';
      btn.textContent = s;
      btn.addEventListener('click', () => {
        chatInput.value = s;
        sendChat();
      });
      container.appendChild(btn);
    });
    chatMessages.appendChild(container);
    chatMessages.scrollTo({ top: chatMessages.scrollHeight, behavior: 'smooth' });
  }

  // Send chat message
  function sendChat() {
    if (!chatInput) return;
    const message = chatInput.value.trim();
    if (!message) return;
    addMessage(message, 'user');
    chatInput.value = '';

    fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    })
      .then(r => r.json())
      .then(data => {
        addMessage(data.reply || 'No response from bot.', 'bot');
        if (data.suggestions && Array.isArray(data.suggestions)) {
          addSuggestions(data.suggestions);
        }
      })
      .catch(() => addMessage('Network error. Try again.', 'bot'));
  }

  // Event listeners for chat
  if (chatSend) chatSend.addEventListener('click', sendChat);
  if (chatInput) chatInput.addEventListener('keydown', e => {
    if (e.key === 'Enter') sendChat();
  });

  // Quiz submission handler (if on quiz page)
  const submitBtn = document.getElementById('submit-quiz');
  if (submitBtn) {
    submitBtn.addEventListener('click', () => {
      const form = document.getElementById('quiz-form');
      if (!form) return;

      const inputs = form.querySelectorAll('input[type=radio]:checked');
      const answers = {};
      inputs.forEach(inp => {
        const name = inp.name.replace(/^q/, '');
        answers[name] = inp.value;
      });

      const path = window.location.pathname.split('/');
      const lessonId = path[path.length - 1];

      fetch(`/submit-quiz/${lessonId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers })
      })
        .then(r => r.json())
        .then(data => {
          const resDiv = document.getElementById('quiz-result');
          if (!resDiv) return;
          resDiv.style.display = 'block';
          resDiv.innerHTML = `<strong>Score: ${data.score} / ${data.total}</strong><br/>`;
          data.feedback.forEach(f => {
            resDiv.innerHTML += `<div>Q${f.id}: ${f.correct ? 'Correct' : 'Wrong'} (Answer: ${f.correct_answer})</div>`;
          });
        })
        .catch(() => alert('Error submitting quiz.'));
    });
  }
});
