// multi_agent_collaboration.js

import { AgentState, ToolNode, StateGraph } from 'langchain_core';
import { TavilySearchResults } from 'langchain_community/tools/tavily_search';
import { PythonREPL } from 'langchain_experimental/utilities';

// Define tools
const tavily_tool = new TavilySearchResults({ max_results: 5 });
const repl = new PythonREPL();

function python_repl(code) {
    try {
        const result = repl.run(code);
        return `Successfully executed:\n\`\`\`python\n${code}\n\`\`\`\nStdout: ${result}`;
    } catch (e) {
        return `Failed to execute. Error: ${e}`;
    }
}

// Create agents
function create_agent(name, tools, system_message) {
    // Placeholder for the agent creation logic
    console.log(`Agent ${name} created with tools: ${tools}`);
}

// Set up agents
const agents = [
    { name: "Researcher", tools: [tavily_tool], system_message: "Gather AI news." },
    { name: "chart_generator", tools: [python_repl], system_message: "Generate charts from data." }
];

// Initialize the graph
const workflow = new StateGraph(AgentState);
agents.forEach(agent_info => {
    const agent = create_agent(agent_info.name, agent_info.tools, agent_info.system_message);
    workflow.add_node(agent_info.name, agent);
});

workflow.add_node("call_tool", new ToolNode([tavily_tool, python_repl]));
workflow.set_entry_point(agents[0].name);
workflow.compile();

// Stream events through the workflow
workflow.stream({
    messages: [{ content: "Fetch the latest AI news and generate a report." }],
    recursion_limit: 150,
});
