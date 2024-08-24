// app.js

// Initialize the game components
let gameStarted = false;
let agents = [];
let gameCanvas, context, spaceship;
let bullets = [];
let asteroids = [];
let currentMode = 1; // Game mode: 1 - Single, 2 - Swarm, 3 - Autonomous Swarm

// Hand gesture and voice command controls
let leftHand, rightHand, voiceCommands = [];

// Audio and visualization variables
let audioContext, analyser, dataArray;

// Function to initialize the game
function initializeGame() {
    gameCanvas = document.getElementById('game-canvas');
    gameCanvas.width = window.innerWidth;
    gameCanvas.height = window.innerHeight;
    context = gameCanvas.getContext('2d');

    // Initialize agents, asteroids, spaceship, and audio context
    initializeAgents();
    initializeAsteroids();
    initializeSpaceship();
    initAudio();

    // Start listening for hand gestures and voice commands
    setupWebSockets();
    setupVoiceCommands();
}

// Function to initialize agents (swarm bots)
function initializeAgents() {
    for (let i = 0; i < 5; i++) {
        agents.push({
            x: Math.random() * gameCanvas.width,
            y: Math.random() * gameCanvas.height,
            tool: 'explore_new_world',
            state: 'idle' // idle, exploring, combat
        });
    }
}

// Function to initialize asteroids
function initializeAsteroids() {
    for (let i = 0; i < 20; i++) {
        asteroids.push({
            x: Math.random() * gameCanvas.width,
            y: Math.random() * gameCanvas.height,
            size: Math.random() * 50 + 20,
            velocity: {
                x: Math.random() * 2 - 1,
                y: Math.random() * 2 - 1
            }
        });
    }
}

// Function to initialize the player spaceship
function initializeSpaceship() {
    spaceship = {
        x: gameCanvas.width / 2,
        y: gameCanvas.height / 2,
        velocity: { x: 0, y: 0 },
        size: 40,
        boost: false
    };
}

// Function to set up the audio context and analyzer for visualization
function initAudio() {
    try {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;
        const bufferLength = analyser.frequencyBinCount;
        dataArray = new Uint8Array(bufferLength);

        const source = audioContext.createMediaElementSource(document.getElementById('audio-element')); // Assuming there's an HTML audio element with id 'audio-element'
        source.connect(analyser);
        analyser.connect(audioContext.destination);
    } catch (error) {
        console.error('Audio context setup failed:', error);
    }
}

// Function to update the game state
function updateGame() {
    if (!gameStarted) return;

    // Clear the canvas for redrawing
    context.clearRect(0, 0, gameCanvas.width, gameCanvas.height);

    // Update player and AI agents based on the current mode
    switch (currentMode) {
        case 1:
            updateSingleAgentMode();
            break;
        case 2:
            updateSwarmMode();
            break;
        case 3:
            updateAutonomousSwarmMode();
            break;
    }

    // Render asteroids, bullets, and spaceship
    renderAsteroids();
    renderBullets();
    renderSpaceship();

    // Animate the audio visualization
    animateVisualization();

    requestAnimationFrame(updateGame);
}

// Update single-agent mode logic
function updateSingleAgentMode() {
    // Handle movement and shooting
    handlePlayerControls();

    // Collision detection between spaceship and asteroids
    handleCollisions();
}

// Update swarm mode logic
function updateSwarmMode() {
    // Handle player controls
    handlePlayerControls();

    // Agents follow the player’s lead, assisting with tasks
    agents.forEach(agent => {
        if (agent.state === 'idle') {
            agent.x += (spaceship.x - agent.x) * 0.05;
            agent.y += (spaceship.y - agent.y) * 0.05;
        }
        renderAgent(agent);
    });
}

// Update autonomous swarm mode logic
function updateAutonomousSwarmMode() {
    // Agents act autonomously to explore, fight, and collect resources
    agents.forEach(agent => {
        if (agent.state === 'exploring') {
            agent.x += Math.random() * 4 - 2;
            agent.y += Math.random() * 4 - 2;
        }
        renderAgent(agent);
    });
}

// Render the spaceship
function renderSpaceship() {
    context.fillStyle = "#00FF00";
    context.beginPath();
    context.arc(spaceship.x, spaceship.y, spaceship.size, 0, Math.PI * 2);
    context.fill();
}

// Render asteroids
function renderAsteroids() {
    asteroids.forEach(asteroid => {
        context.fillStyle = "#FF4500";
        context.beginPath();
        context.arc(asteroid.x, asteroid.y, asteroid.size, 0, Math.PI * 2);
        context.fill();

        // Move asteroids
        asteroid.x += asteroid.velocity.x;
        asteroid.y += asteroid.velocity.y;

        // Handle boundary wrapping
        if (asteroid.x < 0) asteroid.x = gameCanvas.width;
        if (asteroid.x > gameCanvas.width) asteroid.x = 0;
        if (asteroid.y < 0) asteroid.y = gameCanvas.height;
        if (asteroid.y > gameCanvas.height) asteroid.y = 0;
    });
}

// Render bullets
function renderBullets() {
    bullets.forEach(bullet => {
        context.fillStyle = "#FFFF00";
        context.beginPath();
        context.arc(bullet.x, bullet.y, 5, 0, Math.PI * 2);
        context.fill();

        // Move bullets
        bullet.x += bullet.velocity.x;
        bullet.y += bullet.velocity.y;

        // Remove bullets that go off-screen
        if (bullet.x < 0 || bullet.x > gameCanvas.width || bullet.y < 0 || bullet.y > gameCanvas.height) {
            bullets = bullets.filter(b => b !== bullet);
        }
    });
}

// Render AI agent
function renderAgent(agent) {
    context.fillStyle = "#0000FF";
    context.beginPath();
    context.arc(agent.x, agent.y, 20, 0, Math.PI * 2);
    context.fill();
}

// Handle player controls
function handlePlayerControls() {
    if (leftHand && rightHand) {
        // Move spaceship based on hand gesture data
        spaceship.x += (leftHand.x - 0.5) * 20;
        spaceship.y += (leftHand.y - 0.5) * 20;

        // Shooting with right hand gesture
        if (rightHand.touches.index_thumb) shoot();
        if (rightHand.touches.pinky_thumb) spaceship.boost = true;
    } else {
        // Fallback to keyboard controls
        console.warn("Keyboard controls not implemented.");
    }

    // Handle boosting
    if (spaceship.boost) {
        spaceship.velocity.x *= 1.2;
        spaceship.velocity.y *= 1.2;
        spaceship.boost = false;
    }
}

// Handle collision detection between spaceship and asteroids
function handleCollisions() {
    asteroids.forEach(asteroid => {
        const dist = Math.hypot(asteroid.x - spaceship.x, asteroid.y - spaceship.y);
        if (dist < asteroid.size + spaceship.size) {
            // Handle collision (e.g., reduce spaceship health, destroy asteroid)
            console.log("Collision detected!");
        }
    });
}

// Shooting logic
function shoot() {
    const bullet = {
        x: spaceship.x,
        y: spaceship.y,
        velocity: {
            x: Math.cos(spaceship.angle) * 10,
            y: Math.sin(spaceship.angle) * 10
        }
    };
    bullets.push(bullet);
}

// Animate the audio visualization
function animateVisualization() {
    analyser.getByteFrequencyData(dataArray);
    context.fillStyle = '#333';
    dataArray.forEach((value, index) => {
        const barHeight = value * 1.5;
        const x = index * 4;
        context.fillRect(x, gameCanvas.height - barHeight, 2, barHeight);
    });
}

// WebSockets to receive hand gesture data
function setupWebSockets() {
    try {
        const socket = new WebSocket("ws://localhost:6789");

        socket.onmessage = function(event) {
            const data = JSON.parse(event.data);
            leftHand = data.left;
            rightHand = data.right;
        };

        socket.onerror = function(error) {
            console.error("WebSocket Error: ", error);
        };

        socket.onclose = function() {
            console.warn("WebSocket connection closed. Reconnecting...");
            setTimeout(setupWebSockets, 1000);
        };
    } catch (error) {
        console.error("Error setting up WebSocket:", error);
    }
}

// Setup voice command handling
function setupVoiceCommands() {
    console.log("Voice command system initialized");
    // Use WebSockets or AJAX to communicate with the Flask server for voice commands
}

// Event listeners for UI controls
document.getElementById('start-button').onclick = function() {
    gameStarted = true;
    updateGame();
};

document.getElementById('pause-button').onclick = function() {
    gameStarted = false;
};

document.getElementById('reset-button').onclick = function() {
    gameStarted = false;
    agents = [];
    bullets = [];
    asteroids = [];
    initializeGame();
};

// Full-screen handling
window.addEventListener('resize', () => {
    gameCanvas.width = window.innerWidth;
    gameCanvas.height = window.innerHeight;
    updateGame();
});

// Start the game on page load
initializeGame();

}
