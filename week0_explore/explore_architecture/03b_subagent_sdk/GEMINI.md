# Project Rules & Guidelines

Welcome to the `03b_subagent_sdk` workspace. This project contains experiments and implementations for programmatically orchestrating AI agents using the Google Gemini ADK.

## 1. Directory Structure Standards

This workspace is configured as a simplified, code-first Python environment for agent orchestration:

*   `run_agent_adk.py` - Core driver script that uses Gemini ADK `LlmAgent` and `InMemoryRunner` to run the agent.
*   `agent.md` - System instructions and YAML frontmatter metadata for the MUD player agent.
*   `mud_client.py` - Programmatic telnet client to connect to tbaMUD and execute actions.
*   `state_manager.py` - Parser to update character/world status in memory markdown files.
*   `data/` - Local directory containing markdown state memory files:
    *   `data/player_dummy.md` - Isolated state data for dummy.
    *   `data/player_smarty.md` - Isolated state data for smarty.
    *   `data/world.md` - Shared world status map.
*   `.venv/` - Local Python virtual environment containing the `google-adk` package.
*   `.env` - Environment file storing API key credentials.

---

## 2. Coding Guidelines for Agents

When developing or modifying agent logic in this workspace:

### Code-First Design
*   Define agent prompts in `agent.md` and parse them programmatically to construct `LlmAgent` instances.
*   Expose gameplay and helper actions as python function tools to bind directly to the agent.
*   Use `InMemoryRunner.run_async()` to drive the session step-by-step.

### Modularity
*   Keep the MUD connection client isolated from the state parsing logic.
*   Use the state manager context locks to guarantee concurrent safety during execution.
