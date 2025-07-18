document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('debate-form');
    const topicInput = document.getElementById('topic-input');
    const startButton = document.getElementById('start-button');
    const transcriptArea = document.getElementById('transcript-area');
    const agentProfilesDiv = document.getElementById('agent-profiles');

    const agentColors = [
        { bg: '#6a1b9a', border: '#ab47bc' }, // Purple
        { bg: '#00695c', border: '#26a69a' }, // Teal
        { bg: '#c62828', border: '#ef5350' }  // Red
    ];
    let agents = {};
    let agentCounter = 0;

    const typewriter = (element, text, callback) => {
        let i = 0;
        element.innerHTML = "";
        const interval = setInterval(() => {
            if (i < text.length) {
                element.innerHTML += text.charAt(i);
                i++;
                transcriptArea.scrollTop = transcriptArea.scrollHeight;
            } else {
                clearInterval(interval);
                if (callback) callback();
            }
        }, 20); // Adjust typing speed here (milliseconds)
    };

    const addMessage = (sender, content, isStatus = false) => {
        if (isStatus) {
            const statusDiv = document.createElement('div');
            statusDiv.className = 'status-message';
            statusDiv.innerHTML = `<p>${content}</p>`;
            transcriptArea.insertBefore(statusDiv, transcriptArea.firstChild);
            return;
        }

        const messageContainer = document.createElement('div');
        messageContainer.className = 'message-container';

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.style.backgroundColor = agents[sender].color.bg;

        const senderName = document.createElement('p');
        senderName.className = 'sender-name';
        senderName.textContent = sender;

        const contentP = document.createElement('p');
        bubble.appendChild(senderName);
        bubble.appendChild(contentP);
        messageContainer.appendChild(bubble);
        transcriptArea.insertBefore(messageContainer, transcriptArea.firstChild);

        return contentP;
    };

    const handleStreamData = (data) => {
        switch (data.type) {
            case 'agent_stance':
                if (!agents[data.name]) {
                    const color = agentColors[agentCounter % agentColors.length];
                    agents[data.name] = { id: `agent-${agentCounter}`, color: color };
                    
                    const profile = document.createElement('div');
                    profile.className = 'agent-profile';
                    profile.id = agents[data.name].id;
                    
                    const avatar = document.createElement('div');
                    avatar.className = 'avatar';
                    avatar.style.backgroundColor = color.bg;
                    avatar.textContent = data.name.charAt(0); // Initial
                    
                    const name = document.createElement('div');
                    name.className = 'agent-name';
                    name.textContent = data.name;

                    profile.appendChild(avatar);
                    profile.appendChild(name);
                    agentProfilesDiv.appendChild(profile);
                    agentCounter++;
                }
                break;
            
            case 'status':
                Object.values(agents).forEach(agent => {
                    document.getElementById(agent.id)?.classList.remove('thinking');
                });

                if (data.content.includes('is thinking...')) {
                    const agentName = data.content.split(' ')[0];
                    if (agents[agentName]) {
                        document.getElementById(agents[agentName].id)?.classList.add('thinking');
                    }
                }
                break;

            case 'argument':
                const agentName = data.name;
                const agentProfile = document.getElementById(agents[agentName].id);
                if (agentProfile) agentProfile.classList.remove('thinking');
                
                const messageElement = addMessage(agentName, '');
                typewriter(messageElement, data.content);
                break;

            case 'error':
                addMessage('System', data.content, true);
                break;
        }
    };

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const topic = topicInput.value.trim();
        if (!topic) return;

        // Reset UI
        transcriptArea.innerHTML = '';
        agentProfilesDiv.innerHTML = '';
        agents = {};
        agentCounter = 0;
        startButton.disabled = true;
        addMessage('System', 'Initializing debate...', true);

        try {
            const response = await fetch('http://127.0.0.1:8000/debate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic: topic }),
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value);
                const lines = chunk.split('\n\n').filter(line => line.trim());

                lines.forEach(line => {
                    if (line.startsWith('data: ')) {
                        handleStreamData(JSON.parse(line.substring(6)));
                    }
                });
            }
        } catch (error) {
            addMessage('System', 'Error connecting to the server.', true);
        } finally {
            startButton.disabled = false;
            addMessage('System', 'Debate concluded.', true);
            Object.values(agents).forEach(agent => {
                document.getElementById(agent.id)?.classList.remove('thinking');
            });
        }
    });
});
