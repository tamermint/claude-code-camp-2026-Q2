# Week 1 Technical Documentation

## Technical Goal

The technical goal of week 1 is to build a baseline AI agent that can login to the tbaMUD and play on behalf of a user and fulfill goals provided by the user. The player AI agent (codenamed `Boukensha`) must be able to login to the MUD, level up via exploration or by defeating characters and be able to fulfill goals. It must also be able to keep a track of the user state and world state and also be able to log gameplay information. 

The architecture we are exploring here is we are utilising a custom agentic loop that will involve low level calls to the model and it will have a multi-provider setup (so we can swap providers if needed). We are trying to stick to standard libraries as much as we to avoid implementation complexity wherever possible. 

## Technical Uncertainty

- Using custom agentic architecture might mean developing additional systems in place i.e. guardrails, context, memory, prompt routers etc. not sure if this will be feasible as a template for my financial advisor


## Observations

### 00_Config
- `base.rb` is the base class which loads the settings for a specific task and then we have a `player.rb` task that is the player agent. 
- Used Gemini to port over the code to python. Not sure why it always wants to install via the --break-system-packages flag and I need to explicitly ask it to contain it within a .venv
- Gemini ported using `@classmethods` to exactly mirror the Ruby implementation for the tasks and base class

### 01_struct_skeleton
- While porting over to python Gemini did not consider that `00_config` was already ported and it was redoing a few steps.
- Python's dataclass object type was chosen for the tool, message and context struct implementation in Ruby. 

### 02_the_registry
- The registry is basically a way for the agent to register or call a tool to perform player action in the tbaMUD
- The registry is responsible for dispatching tools as well
- Tool registration used to live in context but then we fixed it to ensure it lives in Registry : 
```ruby
attr_reader :tools

    def initialize
      @tools = {}
    end

    def register_tool(tool)
      @tools[tool.name] = tool
    end

    def tool(name, description:, parameters: {}, &block)
      tool = Tool.new(name.to_s, description, parameters, block)
      register_tool(tool)
      tool
    end
    # rest of code...
```
