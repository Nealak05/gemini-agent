# Testing Report — Gemini AI Agent

## Challenges I Encountered During Development

### 1. API Quota Limitations (Regional Restriction)
During initial testing, I encountered a `429 Quota Exceeded` error with `limit: 0` on the Gemini free tier. It turned out to be a regional restriction — the free tier API quota is set to zero for certain regions. I solved this by enabling billing on Google Cloud Console and using a pay-as-you-go API key (which still includes free usage).

### 2. Model Availability
I discovered that some Gemini models (`gemini-1.5-flash`, `gemini-2.0-flash-lite`) are no longer available to new users. After trying several options, the working model for my implementation is `gemini-2.5-flash`.

### 3. PowerShell Environment Variable Syntax
I learned that setting environment variables in PowerShell requires `$env:GEMINI_API_KEY="key"` (with quotes), unlike `cmd.exe` which uses `set GEMINI_API_KEY=key`. When I forgot the quotes, it caused a `CommandNotFoundException`. This was a small but important lesson about platform-specific syntax.

---

## Test Session Transcript

Below is a full testing session where I demonstrate all features of the agent.

### Test 1: Direct Conversation (No Tool Needed)

```
You: hi
A: Hello! How can I help you today?
```

Here the agent recognized this as a simple greeting and responded directly without calling any tool. This shows the agent can distinguish when a tool is needed and when it is not.

### Test 2: Calculator Tool

```
You: What is 100 * 55 + 3?
  [tool_call] Calling tool: calculator({'expression': '100 * 55 + 3'})
  [tool_result] Tool 'calculator' returned: Result: 5503
A: 100 * 55 + 3 = 5503
```

The agent autonomously decided to use the calculator tool and returned the correct result.

### Test 3: Weather Tool

```
You: What's the weather in Baku?
  [tool_call] Calling tool: get_weather({'city': 'Baku'})
  [tool_result] Tool 'get_weather' returned: Weather in Baku: Partly cloudy, Temperature: 15C (feels like 15C), Humidity: 70%, Wind: 7 km/h
A: The weather in Baku is partly cloudy with a temperature of 15C (feels like 15C). The humidity is 70% and the wind speed is 7 km/h.
```

The agent called the weather tool with the correct city parameter and formatted the raw data into a readable response.

### Test 4: Weather Tool (Multiple Cities)

```
You: ok the with tool for tokyo
  [tool_call] Calling tool: get_weather({'city': 'Tokyo'})
  [tool_result] Tool 'get_weather' returned: Weather in Tokyo: Patchy rain nearby, Temperature: 16C (feels like 16C), Humidity: 76%, Wind: 9 km/h
A: The weather in Tokyo is patchy rain nearby, with a temperature of 16C (feels like 16C). The humidity is 76% and the wind speed is 9 km/h.

You: what about in riga?
  [tool_call] Calling tool: get_weather({'city': 'Riga'})
  [tool_result] Tool 'get_weather' returned: Weather in Riga: Partly cloudy, Temperature: 5C (feels like 5C), Humidity: 70%, Wind: 4 km/h
A: The weather in Riga is partly cloudy, with a temperature of 5C (feels like 5C). The humidity is 70% and the wind speed is 4 km/h.
```

I tested the weather tool with multiple cities to make sure it works consistently. The agent also handled a follow-up question ("what about in riga?") correctly by understanding the context.

### Test 5: Time Tool

```
You: What time is it in Tokyo?
  [tool_call] Calling tool: get_time({'timezone': 'Asia/Tokyo'})
  [tool_result] Tool 'get_time' returned: Current time in Asia/Tokyo: 2026-03-30 05:39:58 JST
A: The current time in Tokyo is 05:39:58 JST on 2026-03-30.
```

The agent correctly mapped "Tokyo" to the `Asia/Tokyo` timezone identifier on its own.

### Test 6: Translator Tool

```
You: ok translate hello to french without tool
A: Hello in French is "Bonjour."

You: with tool?
  [tool_call] Calling tool: translate({'text': 'hello', 'source_language': 'en', 'target_language': 'fr'})
  [tool_result] Tool 'translate' returned: Translation (en -> fr): bonjour
A: The translation of "hello" to French is "bonjour".
```

This was an interesting test. I first asked the agent to translate without using a tool, and it answered from its own knowledge. Then I asked "with tool?" and it used the translator tool. This demonstrates **adaptive execution** — the agent decides autonomously whether to use a tool or answer directly based on the user's request.

### Test 7: Agent Answering Without Tools

```
You: how are u?
A: I'm doing well, thank you for asking! I'm ready to assist you with any questions or tasks you have.

You: how old are u?
A: I do not have a name or age. I am a large language model, trained by Google.

You: answer what is weather in baku without using tool
A: I apologize, but I cannot provide real-time weather information for Baku without using my weather tool. As an AI, I don't have access to current, live data without utilizing my designated tools.
```

I tested the agent with conversational questions that don't require tools. It correctly identified that general questions don't need tools, but when I asked for real-time weather data without a tool, it honestly explained that it cannot provide live data without its tools.

### Test 8: Agent Explaining Its Own Architecture

```
You: whyat about tool u use for example when i ask what is the weather
A: When you ask me something like "What is the weather in Baku?", I recognize that this type of
   question requires real-time information that I don't inherently possess. To answer it, I use
   a specific tool from my available set, in this case, a "get weather" tool.

   Here's a simplified breakdown of what happens:
   1. Understand the Request: I analyze your question and identify keywords like "weather" and "Baku".
   2. Identify the Right Tool: I determine that the "get weather" tool is designed for this.
   3. Call the Tool: I execute the "get weather" tool, passing "Baku" as the city parameter.
   4. Receive the Result: The tool connects to an external service and fetches the data.
   5. Formulate the Answer: I take that raw data and present it clearly.
```

I found it interesting that the agent was able to explain the ReAct (Reason → Act → Observe) loop from its own perspective. The steps it described match exactly how I implemented the agent loop in `agent.py`.

### Test 9: Conversation Memory

```
You: my name is ayhkhan
A: It's nice to meet you, Ayhkhan!

You: what is my name?
A: Your name is Ayhkhan.
```

The agent remembered my name within the same session, which confirms that the `MemoryManager` is working correctly and conversation history is being passed to Gemini.

### Test 10: Memory Clear

```
You: clear
Conversation history cleared.

You: what is my name?
A: I do not know your name. I am a large language model, not a personal assistant with access to your personal information.
```

After I cleared the history, the agent no longer remembered my name. This confirms that the `MemoryManager.clear()` method works correctly and the agent truly relies on conversation history for context — it has no hidden memory.

### Test 11: Simple Math Without Tool

```
You: what is 2 + 8 ?
  [tool_call] Calling tool: calculator({'expression': '2 + 8'})
  [tool_result] Tool 'calculator' returned: Result: 10
A: 2 + 8 equals 10.

You: without tool
A: 2 + 8 is 10.
```

When I explicitly asked to answer without a tool, the agent used its own knowledge instead of calling the calculator. This shows the agent adapts its behavior based on user instructions.

### Test 12: Agent Knows Its Own Limitations (Can vs Cannot Answer Without Tools)

One of the most interesting things I noticed during testing is that the agent understands when it can answer on its own and when it truly needs a tool:

**Can answer without tool — simple math:**
```
You: what is 2 + 8 ?
  [tool_call] Calling tool: calculator({'expression': '2 + 8'})
  [tool_result] Tool 'calculator' returned: Result: 10
A: 2 + 8 equals 10.

You: without tool
A: 2 + 8 is 10.
```

**Can answer without tool — translation from its own knowledge:**
```
You: ok translate hello to french without tool
A: Hello in French is "Bonjour."
```

**Cannot answer without tool — real-time weather data:**
```
You: answer what is weather in baku without using tool
A: I apologize, but I cannot provide real-time weather information for Baku without using my
   weather tool. As an AI, I don't have access to current, live data without utilizing my
   designated tools.
```

This shows a key distinction: the agent can answer simple facts (math, common translations) from its own training data, but it honestly refuses to guess when real-time information is required. It knows its own limitations, which is exactly the kind of adaptive behavior the ReAct architecture is designed to produce.

---

## Error Handling Tests

### API Error (Quota Exceeded)
```
You: hi
  [api_error] API Error: 429 You exceeded your current quota...
A: Sorry, I encountered an error communicating with the AI model: 429 You exceeded your current quota...
```
The agent did not crash — it displayed a helpful error message and continued running, allowing me to try again.

### Model Not Found
```
You: hi
  [api_error] API Error: 404 models/gemini-1.5-flash is not found...
A: Sorry, I encountered an error communicating with the AI model: 404 models/gemini-1.5-flash is not found...
```
This was also handled gracefully with an informative error message. The agent kept running without crashing.

---

## Summary of Test Results

| Test | Feature | Result |
|------|---------|--------|
| Direct conversation | No tool needed | PASS |
| Calculator | Tool: calculator | PASS |
| Weather (multiple cities) | Tool: get_weather | PASS |
| Time zones | Tool: get_time | PASS |
| Translation | Tool: translate | PASS |
| Adaptive execution | With/without tool | PASS |
| Conversation memory | Remember context | PASS |
| Memory clear | Reset history | PASS |
| API error handling | 429/404 errors | PASS |
| Agent self-explanation | Describes ReAct loop | PASS |
| Knows its limitations | Can vs cannot without tools | PASS |
