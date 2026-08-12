# Coding & Implementation Standards

These rules apply to code implementation and testing processes in the `03_subagent_sdk` project.

## Code Quality & Style
1. **Language**: Use Python or Node.js/JavaScript/TypeScript for scripting.
2. **Readability**: Write self-documenting code with clear variable and function names. Keep functions small and modular.
3. **Docstrings**: Retain existing docstrings and comments. When writing new code, document public interfaces clearly.

## Testing & Validation
1. **Unit Tests**: Always verify code changes with local tests.
2. **Execution Logs**: Output structured logs (preferably in JSON) for scripts run by agents, making it easy for the agent to parse status.
3. **Graceful Degradation**: Ensure that network timeouts or external tool failures are handled gracefully without crashing the parent process.
