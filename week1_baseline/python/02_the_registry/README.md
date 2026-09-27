# The Tool Registry

The Tool Registry is how BOUKENSHA manages what capabilities the agent can use. 

It has two jobs: 
  1. storing tools
  2. dispatching tools when asked

## New Files

| File | Description |
|---|---|
| `boukensha/registry.py` | The Registry class — registers tools and dispatches calls |
| `boukensha/errors.py` | BOUKENSHA-specific error classes (`UnknownToolError`) |

## How It Works

The agent NEVER calls a tool directly. 
It emits a structured request (name and args) and the Registry looks up the tool and runs it. 

```
Agent:  "Hey registry call move with direction='north'"
Registry: "looking up 'move' in the tool table"
Registry: "Found it now calling the block with the provided args"
Registry: "Here's the result"
Agent: "Thanks buddy"
Registry: "Thats why you pay me the big tokens"
```

## Boukensha::Registry (Python: `Registry`)

| Method | Description |
|---|---|
| `tool(name, description, parameters, block)` | Registers a new tool (supports both decorator syntax `@registry.tool(...)` and callable `block`) |
| `dispatch(name, args)` | Looks up a tool by name and calls it with the provided keyword arguments |

## Boukensha::UnknownToolError (Python: `UnknownToolError`)

Raised when `dispatch` is called with a name that has no registered tool. 
A harness needs explicit error boundaries — an unrecognised tool name should never silently fail.

**Example:**
```
UnknownToolError: No tool registered as 'flee'
```

## Expected Output

```
=== BOUKENSHA Step 2: Tool Registry ===

Config:  #<Boukensha::Config dir=... tasks=player>
Context: #<Context task=player turns=0>
Tools:
  #<Tool name=move description=Move the player in a direction (north, so params=[:direction]>
  #<Tool name=shout description=Shout a message so everyone in the zone c params=[:message]>

Dispatching 'shout' with message='dragon spotted'...
Result: DRAGON SPOTTED

Dispatching 'move' with direction='north'...
Result: You move north into a torch-lit corridor.

UnknownToolError caught: No tool registered as 'flee'
```

## Run Example

```sh
./bin/python/02_the_registry.sh
```
