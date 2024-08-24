export function switchGameMode(mode) {
    switch (mode) {
        case 1:
            console.log("Single-agent mode activated");
            break;
        case 2:
            console.log("Swarm mode activated");
            break;
        case 3:
            console.log("Autonomous swarm mode activated");
            break;
        default:
            console.log("Unknown mode");
    }
}

// Attach to the global window object if not using modules
window.switchGameMode = switchGameMode;
