const chatInput = document.querySelector('.ai-chat-input input');
const chatButton = document.querySelector('.ai-chat-input button');
const chatMessages = document.querySelector('.ai-chat-messages');
const exerciseTabs = document.querySelectorAll('.exercise-tab');
const exerciseContent = document.querySelector('.exercise-content');
const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
const navMenu = document.querySelector('.nav-menu');
const levelProgressFill = document.getElementById('level-progress-fill');
const levelProgressText = document.getElementById('level-progress-text');

let conversation = [];
let currentExercises = null;
let currentPracticeType = null;
let currentTargetLanguage = null;
let currentLevel = null;
let levelProgress = 0;

function appendMessage(text, role) {
    if (!chatMessages) return;
    const div = document.createElement('div');
    div.classList.add(role === 'user' ? 'user-message' : 'ai-message');
    div.textContent = text;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    conversation.push({ role: role === 'user' ? 'user' : 'assistant', content: text });
}

function setActiveTab(type) {
    if (!exerciseTabs) return;
    exerciseTabs.forEach(tab => {
        const t = tab.getAttribute('data-tab');
        tab.classList.toggle('active', t === type);
    });
}

function setLevelProgress(value) {
    levelProgress = Math.max(0, Math.min(100, value));
    if (levelProgressFill) levelProgressFill.style.width = levelProgress + '%';
    if (levelProgressText) levelProgressText.textContent = Math.round(levelProgress) + '%';
}

function addLevelProgress(delta) {
    setLevelProgress(levelProgress + delta);
    if (levelProgress >= 100) {
        conversation.push({
            role: 'user',
            content: 'System note: learner has filled the level progress bar. Please slightly increase the difficulty of the next exercises.'
        });
        setLevelProgress(0);
    }
}

function renderExercises(type, items) {
    currentPracticeType = type;
    currentExercises = items;

    if (!exerciseContent) return;
    exerciseContent.innerHTML = '';
    if (!items || !items.length) return;

    setActiveTab(type);

    items.forEach(item => {
        const wrapper = document.createElement('div');
        wrapper.className = 'exercise-item';
        wrapper.dataset.id = item.id;

        const q = document.createElement('div');
        q.className = 'exercise-question';
        q.textContent = item.question || '';
        wrapper.appendChild(q);

        if (item.options && item.options.length) {
            const optsWrap = document.createElement('div');
            optsWrap.className = 'exercise-options';

            item.options.forEach((opt, i) => {
                const optDiv = document.createElement('div');
                optDiv.className = 'exercise-option';

                const input = document.createElement('input');
                input.type = 'radio';
                input.name = item.id;
                input.dataset.index = String(i);

                const label = document.createElement('label');
                label.textContent = opt;

                optDiv.appendChild(input);
                optDiv.appendChild(label);
                optsWrap.appendChild(optDiv);
            });

            wrapper.appendChild(optsWrap);
        }

        exerciseContent.appendChild(wrapper);
    });

    const submitBtn = document.createElement('button');
    submitBtn.className = 'exercise-submit';
    submitBtn.textContent = 'Submit Test';
    submitBtn.addEventListener('click', submitTestToAI);
    exerciseContent.appendChild(submitBtn);
}

function collectUserAnswers() {
    const answers = {};
    const items = document.querySelectorAll('.exercise-item');
    items.forEach(item => {
        const id = item.dataset.id;
        const checked = item.querySelector('input[type="radio"]:checked');
        answers[id] = checked ? Number(checked.dataset.index) : null;
    });
    return answers;
}

async function submitTestToAI() {
    const chatBlock = document.querySelector('.ai-chat');
    if (chatBlock) chatBlock.scrollIntoView({ behavior: 'smooth' });

    if (!currentExercises) {
        appendMessage('No exercises to check.', 'assistant');
        return;
    }

    const userAnswers = collectUserAnswers();

    const requestBody = {
        answers: userAnswers,
        exercises: currentExercises,
        target_language: currentTargetLanguage,
        estimated_level: currentLevel
    };

    appendMessage('Submitting your answers…', 'assistant');

    try {
        const resp = await fetch('/api/language/check', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });

        if (!resp.ok) {
            appendMessage('Server error while checking answers.', 'assistant');
            return;
        }

        const data = await resp.json();
        if (!data || data.status !== 'success') {
            appendMessage('AI failed to process the test.', 'assistant');
            return;
        }

        const result = data.data;
        if (result.assistant_message) {
            appendMessage(result.assistant_message, 'assistant');
        }

        let correctCount = 0;
        let totalCount = 0;

        if (Array.isArray(result.feedback)) {
            result.feedback.forEach(item => {
                totalCount += 1;
                if (item.correct) correctCount += 1;
                const msg =
                    'Question: ' + item.id + '\n' +
                    'Your answer: ' + (item.user_answer || '—') + '\n' +
                    'Correct answer: ' + (item.correct_answer || '—') + '\n' +
                    'Explanation: ' + (item.explanation || '');
                appendMessage(msg, 'assistant');
            });
        }

        if (totalCount > 0) {
            const accuracy = correctCount / totalCount;
            const percent = Math.round(accuracy * 100);
            appendMessage('Your score: ' + correctCount + '/' + totalCount + ' (' + percent + '%).', 'assistant');
            const delta = accuracy * 40;
            addLevelProgress(delta);
        }
    } catch (e) {
        appendMessage('Connection error while checking answers.', 'assistant');
    }
}

async function sendConversation() {
    try {
        const resp = await fetch('/api/language/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ messages: conversation, ui_language: 'en' })
        });

        if (!resp.ok) {
            appendMessage('Server error while processing the request.', 'assistant');
            return;
        }

        const data = await resp.json();
        if (!data || data.status !== 'success') {
            appendMessage('Failed to receive a response from the assistant.', 'assistant');
            return;
        }

        const payload = data.data || {};

        currentTargetLanguage = payload.target_language || currentTargetLanguage;
        currentLevel = payload.estimated_level || currentLevel;

        if (payload.assistant_message) {
            appendMessage(payload.assistant_message, 'assistant');
        }

        if (payload.exercises && payload.exercises.items && payload.exercises.items.length) {
            const exType = payload.exercises.type || 'vocabulary';
            renderExercises(exType, payload.exercises.items);
        }
    } catch (e) {
        appendMessage('A connection error occurred.', 'assistant');
    }
}

async function initTutor() {
    if (!chatMessages) return;
    chatMessages.innerHTML = '';
    conversation = [];

    try {
        const resp = await fetch('/api/language/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ messages: [], ui_language: 'en' })
        });

        if (!resp.ok) {
            appendMessage('Unable to connect to the language assistant.', 'assistant');
            return;
        }

        const data = await resp.json();
        if (!data || data.status !== 'success' || !data.data) {
            appendMessage('The assistant is unavailable.', 'assistant');
            return;
        }

        const payload = data.data;

        if (payload.assistant_message) {
            appendMessage(payload.assistant_message, 'assistant');
        }

        currentTargetLanguage = payload.target_language || null;
        currentLevel = payload.estimated_level || null;

        if (payload.exercises && payload.exercises.items && payload.exercises.items.length) {
            const exType = payload.exercises.type || 'vocabulary';
            renderExercises(exType, payload.exercises.items);
        }
    } catch (e) {
        appendMessage('Assistant connection error.', 'assistant');
    }
}

async function handleUserMessage() {
    if (!chatInput) return;
    const text = chatInput.value.trim();
    if (!text) return;
    appendMessage(text, 'user');
    chatInput.value = '';
    await sendConversation();
}

if (chatButton) {
    chatButton.addEventListener('click', () => handleUserMessage());
}

if (chatInput) {
    chatInput.addEventListener('keypress', e => {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleUserMessage();
        }
    });
}

if (exerciseTabs && exerciseTabs.length) {
    exerciseTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const type = tab.getAttribute('data-tab');
            appendMessage('I want to practice ' + type + '.', 'user');
            sendConversation();
        });
    });
}

if (mobileMenuBtn && navMenu) {
    mobileMenuBtn.addEventListener('click', () => {
        navMenu.classList.toggle('active');
        mobileMenuBtn.innerHTML = navMenu.classList.contains('active')
            ? '<i class="fas fa-times"></i>'
            : '<i class="fas fa-bars"></i>';
    });
}

fetch('/header.html')
    .then(response => {
        if (!response.ok) throw new Error('HTTP error: ' + response.status);
        return response.text();
    })
    .then(html => {
        const headerContainer = document.getElementById('header-container');
        if (headerContainer) headerContainer.innerHTML = html;
    })
    .catch(error => {
        const headerContainer = document.getElementById('header-container');
        if (headerContainer) {
            headerContainer.innerHTML =
                '<div style="color: red;">Error loading header: ' + error.message + '</div>';
        }
    });

setLevelProgress(0);
initTutor();
