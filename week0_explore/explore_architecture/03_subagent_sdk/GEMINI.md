# Project Rules & Guidelines

Welcome to the `03_subagent_sdk` workspace. This project contains experiments and implementations for the Subagent SDK within the Claude Code Camp repository.

## 1. Directory Structure Standards

This workspace is configured to follow Gemini's **Antigravity Customization System** standards. Local configuration files are located under the `.agents/` folder:

*   `.agents/rules/` - Directory for contextual rules (applied dynamically based on folder).
*   `.agents/skills/` - Custom skills (progressive disclosure runbooks).
*   `.agents/mcp_config.json` - MCP Server integration config.
*   `.agents/hooks.json` - Agent execution loop lifecycle hooks.

---

## 2. Coding Guidelines for Subagents

When developing subagent logic or scripts in this workspace:

### Modularity
*   Keep subagents focused on a single responsibility.
*   Use standard input/output (stdin/stdout) streams or structured payloads for communication.

### Error Handling & Reliability
*   Implement clean error codes and descriptive message formats.
*   Add validation/sanity checks before invoking subagent scripts.
*   Ensure all long-running processes gracefully terminate under timeouts.

---

## 3. Customization Framework Reference

For details on extending agent behavior:
*   **Rules**: Create markdown files in `.agents/rules/*.md`.
*   **Skills**: Create a directory in `.agents/skills/<name>/` with a `SKILL.md` frontmatter file.
*   **MCP Servers**: Define tool integrations in `.agents/mcp_config.json`.
