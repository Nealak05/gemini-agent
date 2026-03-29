"""
Agent — Orchestrates the ReAct (Reason → Act → Observe) loop.

The Agent receives user input, sends it to Google Gemini along with
conversation history and tool declarations, and processes the response.
If the LLM decides to call a tool, the Agent executes it via the
ToolRegistry and feeds the result back until a final text answer is produced.
"""

import google.generativeai as genai
from google.generativeai.types import content_types

from gemini_agent.memory import MemoryManager
from gemini_agent.registry import ToolRegistry
from gemini_agent.observer import EventManager


# Maximum number of tool-call rounds before forcing a text response
MAX_ITERATIONS = 10

SYSTEM_INSTRUCTION = (
    "You are a helpful personal assistant. You can answer questions directly "
    "or use the available tools when needed. When a tool is appropriate, call it. "
    "When the user asks a conversational question, respond directly without tools. "
    "Always provide clear, helpful responses."
)


class Agent:
    """AI Agent that implements the ReAct pattern.

    Coordinates between the Gemini model, ToolRegistry, MemoryManager,
    and EventManager to process user requests adaptively.
    """

    def __init__(
        self,
        registry: ToolRegistry,
        memory: MemoryManager,
        event_manager: EventManager,
        model_name: str = "gemini-2.5-flash",
    ) -> None:
        """Initialize the Agent.

        Args:
            registry: The ToolRegistry containing available tools.
            memory: The MemoryManager for conversation history.
            event_manager: The EventManager for publishing events.
            model_name: The Gemini model to use.
        """
        self._registry = registry
        self._memory = memory
        self._events = event_manager

        # Build tool declarations for Gemini
        declarations = registry.get_all_declarations()
        tools_config = [{"function_declarations": declarations}] if declarations else None

        self._model = genai.GenerativeModel(
            model_name=model_name,
            tools=tools_config,
            system_instruction=SYSTEM_INSTRUCTION,
        )

    def run(self, user_input: str) -> str:
        """Execute the ReAct loop for a single user message.

        1. Reason — send user input + history to Gemini
        2. Act    — if Gemini returns a function call, execute it
        3. Observe — feed tool result back to Gemini
        4. Repeat  — until a text response is produced

        Args:
            user_input: The user's natural language message.

        Returns:
            The agent's final text response.
        """
        # Add user message to memory
        self._memory.add_message("user", [{"text": user_input}])

        self._events.publish("api_call", {
            "type": "user_input",
            "message": f"User: {user_input}"
        })

        try:
            # Start the conversation with full history
            response = self._model.generate_content(self._memory.get_history())
        except Exception as e:
            error_msg = f"API Error: {e}"
            self._events.publish("error", {"type": "api_error", "message": error_msg})
            return f"Sorry, I encountered an error communicating with the AI model: {e}"

        # ReAct loop: keep processing until we get a text response
        for iteration in range(MAX_ITERATIONS):
            candidate = response.candidates[0]
            part = candidate.content.parts[0]

            # --- Check if the model returned a function call (ACT) ---
            if part.function_call and part.function_call.name:
                func_call = part.function_call
                tool_name = func_call.name
                tool_args = dict(func_call.args) if func_call.args else {}

                self._events.publish("tool_called", {
                    "type": "tool_call",
                    "message": f"Calling tool: {tool_name}({tool_args})"
                })

                # Store the model's function call in memory
                self._memory.add_message("model", [part])

                # --- Execute the tool via the registry (OBSERVE) ---
                result = self._registry.execute_tool(tool_name, **tool_args)

                self._events.publish("tool_result", {
                    "type": "tool_result",
                    "message": f"Tool '{tool_name}' returned: {result}"
                })

                # Build function response and add to memory
                function_response = genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=tool_name,
                        response={"result": result}
                    )
                )
                self._memory.add_message("function", [function_response])

                # --- Send tool result back to Gemini (REASON again) ---
                try:
                    response = self._model.generate_content(self._memory.get_history())
                except Exception as e:
                    error_msg = f"API Error during tool result processing: {e}"
                    self._events.publish("error", {"type": "api_error", "message": error_msg})
                    return f"Sorry, I got a tool result but failed to process it: {e}"

            else:
                # --- Model returned a text response — we're done ---
                final_text = part.text if part.text else "I'm not sure how to respond to that."

                # Store the model's response in memory
                self._memory.add_message("model", [{"text": final_text}])

                self._events.publish("api_call", {
                    "type": "response",
                    "message": f"Agent: {final_text[:100]}..."
                })

                return final_text

        # Safety: if we hit max iterations, return what we have
        return "I've been processing for too long. Please try rephrasing your request."
