function startVoiceRecognition() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onresult = function(event) {
        const command = event.results[0][0].transcript.toLowerCase();
        console.log(`Command received: ${command}`);

        if (command.includes("single agent")) {
            switchGameMode(1);
        } else if (command.includes("swarm")) {
            switchGameMode(2);
        } else if (command.includes("autonomous")) {
            switchGameMode(3);
        } else {
            console.log("Unknown command");
        }
    };

    recognition.start();
}

// Call this function to start voice recognition
startVoiceRecognition();
