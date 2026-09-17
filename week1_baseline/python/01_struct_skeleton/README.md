# The Struct Skeleton (Python Port)

Let's define data structures for specific data we need to constantly pass around in the agentic loop:
- `boukensha.Tool`
- `boukensha.Message`
- `boukensha.Context`

We use standard library `@dataclass` and lightweight classes to represent these data structures cleanly and idiomatically in Python.

---

## Data Structures

### `boukensha.Tool`
Represents an executable tool that the agent can invoke.

| Field | Description |
|---|---|
| `name` | The name of the tool |
| `description` | Shown to the agent so it knows when to invoke the tool |
| `parameters` | The arguments that need to be passed in |
| `block` | The callable function/lambda that runs when the tool is called |

**Example:**
```
#<Tool name=move description=Move the player in a direction (north, so params=[:direction]>
```

### `boukensha.Message`
A single unit of conversation between the user, agent, or tool result.

| Field | Description |
|---|---|
| `role` | Who is speaking (`user`, `assistant`, or `tool_result`) |
| `content` | The text content of the message |
| `tool_use_id` | Links a tool result back to the specific tool call that requested it |

**Example:**
```
#<Message role=user content=Explore north and tell me what you find....>
#<Message role=assistant content=Sure, let me head north and take a look....>
#<Message role=tool_result [toolu_01X] content=You move north into a torch-lit corridor....>
```

### `boukensha.Context`
Holds everything Boukensha needs to make an API call:
- `task`: The task class bound to this context (e.g. `boukensha.tasks.Player`).
- `system`: The system prompt string.
- `messages`: Full conversation history.
- `tools`: Registered tools available to the agent.

**Example:**
```
#<Context task=player turns=2 tools=1>
```

---

## Run Example

```sh
./week1_baseline/bin/python/01_struct_skeleton.sh
```

Expected output:

```
=== Boukensha Step 1: Struct Skeleton ===

Config:   #<Boukensha::Config dir=... tasks=player>
Context:  #<Context task=player turns=2 tools=1>
Tool:     #<Tool name=move description=Move the player in a direction (north, so params=[:direction]>
Messages:
  #<Message role=user content=Explore north and tell me what you find....>
  #<Message role=assistant content=Sure, let me head north and take a look....>
```
