// procedural_generation.js
function generatePlanet() {
    const planetName = generateRandomName();
    const resources = Math.floor(Math.random() * 100);
    const enemyPresence = Math.random() > 0.5;

    return { planetName, resources, enemyPresence };
}

function generateRandomName() {
    const syllables = ['Xar', 'Quo', 'Val', 'Tuk', 'Zim', 'Ark'];
    return syllables[Math.floor(Math.random() * syllables.length)] + 
           syllables[Math.floor(Math.random() * syllables.length)];
}

function generateMission() {
    const missions = ['Explore new planet', 'Defeat enemy fleet', 'Gather rare resources'];
    return missions[Math.floor(Math.random() * missions.length)];
}
