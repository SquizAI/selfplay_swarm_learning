// ai_integration.js
async function fetchAIAction(observation) {
    // Send observation to Python backend and get AI-generated action
    const response = await fetch('/ai_action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ observation })
    });
    const data = await response.json();
    return data.action;
}