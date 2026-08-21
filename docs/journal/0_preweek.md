## Preweek Technical Documentation

## Technical Goal

The technical goal of Preweek (Explore) is to determine which agent architectures fit my project use case for a personalized financial advisor. The personalized financial advisor agent will have access to Context (user transaction data, short-term and long-term financial goals and interest), determine spending habits and help user chart out personalized financial plan.
Technically, the agent architecture must be able to do three things :
 - parse and categorize user data
 - develop personalized semantic and temporal memory states
 - create plan of action

The AI architectures we have explored so far (in increasing order of complexity) : 

- An agent file with referenced files i.e. GEMINI.md, @~/docs/\*.md
- Agent skills driven by main agent e.g. ~/.skills
- Agent skills driven by subagent sdk i.e. Filesystem subagent driven by a coding harness or agent sdk
- AI workflow automation platform e.g. n8n

The AI architecture we are yet to explore : 

- Use low level first-party LLM SDKs that leverages geenric plug and play packages
- Use REST APIs directly and use custom agentic loop 

## Technical Uncertainty

- One of the major concerns is whether using agentic loops fit our purpose? Maybe we use an AI agent but not a coding harness

- Memory and context management is another challenge. If we use coding harness or subagents then the agent has to do multiple tool calls to the memory subsystem to get context. Developing context is a challenge in terms of efficiency

- Scalability, Security and Latency: can't have all three. Which architecture is scalable and secure is another challenge. Maybe latency is not a show stopper as advisor agent can take time to run?

- Is AI's thinking efficient for maintaining long-term user context and taking strategic decisions based on new user states?

## Technical Hypotheses

- So far using APIs to the LLM directly has not been super effective. My [initial work](https://github.com/tamermint/Vektor-State) on this has so far not been entirely fruitful 

- I utilized a object factory to create a user-input object, use a TS math engine to generate a forecast and then send to the LLM. However, it is not token efficient and not dynamic

- I guess coding loops would kind of encompass the same workfow? This will either lead to semantic collapse or make the agent hallucinate

- Maybe custom agentic loops using REST api calls to the base model can help manage isolated context runs but maintaining a core user state is another challenge

- I think what will help is : 
 - User state management and memory via a SQL db and context management via Vector db
 - Caching (redis) for immediate access to most recent user state
 - Specialized agentic loop to drive inference and generate user plans and modify based on user input
 - Generic structure for memory and context to tolerate swapping of agent models or model upgrades

## Technical Observations
- An agent file (GEMINI.md) with referenced files produced unreliable python scripts that did not reliably connect to the game. It also needed a lot of context and manual instructions to even connect to the MUD and login to the game

- Agent skills produced a better outcome in so far due to a better directed context and not just more context. It also attempted to read outside the workspace in order to short-circuit the objective provided by me. Though it still produced unreliable python scripts which did not cater to edge cases. When given a harder goal it did not attempt to "reason" e.g. level up to beat up the minotaur. Instead it just brute forced

- Agent skills driven by sub-agent sdk emitted lots of permission issues. Even while allowing permission to run scripts, it kept asking for permissions. It created a `allow_script` when prompted to update workspace settings but it wasn't successful. It also spawned sub-agents which overrwrote global state information. Using Markdown files was not efficient as simple state memory was not efficient as it kept updating with brittle navigation instructions :
```sh
## Key Locations & Discovered Rooms

| Room Name | Exits | Notable Mobs / Features |
|---|---|---|
| The Temple Of Midgaard | N, E, S, W, D | ATM, Temple Gate |
| The Temple Square | N, E, S, W | Marble Fountain |
| Market Square | N, E, S, W | Peacekeeper, Statue, Cityguard |
| Main Street (West) | N, E, S, W | Bakery (N), Armory (S) |
| The Bakery | S | Baker (Danish 7c, Bread 14c, Waybread 72c) |
| Main Street (Far West) | N, E, S, W | Magic Shop (N), Mages' Guild (S), West Gate (W), Fido |
| Main Street (East) | N, E, S, W | General Store (N), Pet Shop (S) |
| Main Street (Far East) | N, E, S, W | Weapon Shop (N), Guild of Swordsmen (S), East Gate (E), Fido |
| Entrance to Guild of Swordsmen | N, E | Knight Guard, Peacekeeper, ATM |
| Bar of Swordsmen | S, W | Waiter, Bulletin Board |
| Tournament and Practice Yard | N, D | **Guildmaster**, Well leading down |

```

- Agent skills driven by agent definition was slightly better in terms of organizing project directory and was slightly better in executing scripts (due to the explicit use of SDK) though there was no visibility into the progress of the agent gameplay. It did handle concurrent sessions by spawning two agents but then the permissions issued crept back in because permissions are not directly inherited by subagents and they need an explicit `run_command` permissions to run python scripts (in the Agent definition)

- N8N did not execute commands because the setup needed to execute N8N as a workflow was a bit complicated and would not scale well. It needed a sub-workflow to connect from my local machine to the docker container running the MUD and if there are permission issues to run command in the container, then the agentic loop will break

## Technical Conclusions

- Agent skills driven just by a .md file is equivalent to using a coding harness directly. It is useful for producing and reviewing code but not for specialized tasks like executing user goals in a MUD

- Agent skills driven by main agent perform better when context is driven and structured explicitly. They are useful not just for simple tasks and but can execute non-coding tasks of moderate difficulty

- A better system/memory structure is needed for map navigation and world data. 

- Agent skills driven by sub-agent sdk or agent definition perform better than agent skills driven by a main agent for non-coding and specialized tasks. It used plan mode for long running tasks and is able to delegate execution to sub-agents while overseeing task execution. It also produced artifacts for me to review : 
```sh
# Walkthrough: Concurrent Gemini ADK Agents Execution

I have successfully launched and executed two concurrent Gemini ADK subagents (`dummy` and `smarty`) in parallel using `asyncio.gather()` inside our simplified, code-first Python project workspace.

---

## 1. Concurrent Implementation (`run_agent_adk.py`)
I updated [`run_agent_adk.py`](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week0_explore/explore_architecture/03b_subagent_sdk/run_agent_adk.py) to support concurrent executions:
* **Tool Parameterization**: Wrapped the MUD client command execution tool inside a factory closure (`make_execute_mud_commands`) to dynamically bind user-specific login credentials for each agent.
* **Parallel Execution**: Used `asyncio.gather()` to spin up separate `InMemoryRunner` instances and run the two agents concurrently.
* **Prefixing Output**: Prefixed each streaming output line with `[dummy]` or `[smarty]` to keep concurrent outputs clear and readable.

---

## 2. Validation & Findings
When executed, both agents logged in concurrently, checked their respective score sheets, and reported their state:

### dummy Status:
* **Hit Points**: 22 / 22
* **Mana**: 100 / 100
* **Movement**: 80 / 85
* **Gold**: 30 coins
* **Status**: **NOT hungry, NOT thirsty** (no warnings printed in the score vitals).

### smarty Status:
* **Hit Points**: 14 / 14
* **Mana**: 100 / 100
* **Movement**: 83 / 83
* **Gold**: 0 coins
* **Status**: **NOT hungry, NOT thirsty** (no warnings printed in the score vitals).

```
Handling co-op sessions was a new use-case and it did not fail the agentic workflow but we did not consider in the original design. 

- N8N may be better suited for multi-step cloud workflows and may scale well for repeatable and deterministic tasks across multiple instances. It may not scale well for user specific tasks. We did not fully explore N8N architecture due to technical limitations and complexity of implementation. Though one positive outcome was that the agent was able to adapt the script for N8N's tool_call node

## Key Takeaway

- For more specific use cases like playing a MUD game, specialized agentic loops will be needed. In line with my technical goal, I am more inclined towards using the sub-agent infrastructure as an intial starting infrastructure template but solving the memory and context management will be the key challenge  


