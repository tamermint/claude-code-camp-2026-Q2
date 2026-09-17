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
- 