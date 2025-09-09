from langchain_ollama import OllamaLLM
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool
from typing import List, Any
from voice import process_voice_input, speak
from system_monitor import monitoring_tools, ProactiveMonitor
from desktop_automation import desktop_tools
from security_mediator import security_mediator
from feedback_logger import log_feedback
import hotkey_listener
import time

# Set up Ollama LLM integration
llm = OllamaLLM(model="phi3:3.8b")

# Placeholder tool for basic tool calling
class PlaceholderTool(BaseTool):
    name: str = "placeholder_tool"
    description: str = "A placeholder tool for future implementation"

    def _run(self, query: str) -> str:
        return f"Placeholder tool executed with query: {query}"

    async def _arun(self, query: str) -> str:
        return await self._run(query)

# Security wrapper for tools
class SecureTool(BaseTool):
    original_tool: BaseTool

    def __init__(self, original_tool: BaseTool):
        super().__init__(original_tool=original_tool, name=original_tool.name, description=original_tool.description)

    def _run(self, *args, **kwargs) -> str:
        return security_mediator.execute_tool(self.original_tool._run, self.name, *args, **kwargs)

    async def _arun(self, *args, **kwargs) -> str:
        return await security_mediator.execute_tool(self.original_tool._arun, self.name, *args, **kwargs)

# Wrap all tools with security
secure_tools = [SecureTool(tool) for tool in [PlaceholderTool()] + monitoring_tools + desktop_tools]
tools = secure_tools

# Define the agent prompt
prompt = PromptTemplate.from_template("""
You are Jarvis, an AI assistant. Follow the agentic loop: Perceive, Plan, Act, Learn.

You have access to the following tools:
{tools}

Use the following format:
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Current task: {input}

{agent_scratchpad}
""")

# Create the agent
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# Proactive monitoring
def proactive_callback(message):
    speak(message)

monitor = ProactiveMonitor(callback=proactive_callback)

# Define the agentic loop
def perceive() -> str:
    """Perceive: Process voice input and verify speaker."""
    audio = process_voice_input()
    if audio is not None:
        # Placeholder for STT: return dummy transcription
        return "voice command"
    else:
        return None

def plan(perceived_input: str) -> str:
    """Plan: Use LLM to decompose goal into steps."""
    plan_prompt = f"Decompose the following goal into steps: {perceived_input}"
    return llm.invoke(plan_prompt)

def act(plan_output: str) -> str:
    """Act: Execute tools based on plan."""
    # For now, use the agent executor with the plan as input
    result = agent_executor.invoke({"input": plan_output})
    return result["output"]

def learn(action_result: str) -> None:
    """Learn: Incorporate feedback and memory (placeholder)."""
    # Placeholder for future memory implementation
    print(f"Learning from result: {action_result}")

# Main agent loop
def run_agentic_loop() -> str:
    perceived = perceive()
    if perceived is None:
        result = "Access denied"
    else:
        planned = plan(perceived)
        acted = act(planned)
        learn(acted)
        result = acted
    speak(result)
    # Listen for user corrections
    capture_feedback(perceived, result)
    return result

def capture_feedback(original_instruction: str, agent_response: str) -> None:
    """
    Listen for user corrections after responding.
    """
    print("Listening for corrections... (say 'Jarvis, that was wrong' followed by correction)")
    time.sleep(3)  # Wait 3 seconds for user to respond
    correction_audio = process_voice_input()
    if correction_audio is not None:
        # Placeholder: In real implementation, transcribe correction_audio
        # For now, assume transcription is "Jarvis, that was wrong. The correct answer is..."
        transcription = "Jarvis, that was wrong. The correct answer is sunny weather."  # Dummy
        if "that was wrong" in transcription.lower():
            # Extract correction
            correction_start = transcription.lower().find("the correct answer is")
            if correction_start != -1:
                correction = transcription[correction_start + len("the correct answer is"):].strip()
                log_feedback(original_instruction, agent_response, correction)
                speak("Thank you for the correction. I'll learn from this.")
            else:
                speak("Correction not understood. Please try again.")

if __name__ == "__main__":
    # Start proactive monitoring
    monitor.start()
    # Run the agent loop with voice input
    result = run_agentic_loop()
    print(f"Result: {result}")
    # Stop monitoring
    monitor.stop()