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
### 03_prompt_builder
- Google/Gemini has their own way for tool calling, context management etc. 
- State is managed in Boukensha and every conversation with the model is stateless. Is this efficient? Maybe for this use case but based on my initial goal, user state and context management become key when catering for long range pattern data 
- The prompt builder is basically used to build the initial prompt, set the system instruction while conversing with the agent

### 04_api_client
- The client initializes the builder which retains context. The goal was to make it stateless. 
- Made the following changes to ensure the client is stateless. In `client.rb`, the builder is not initialized:
  ```diff

  + def initialize(max_retries: MAX_RETRIES, base_retry_delay: BASE_RETRY_DELAY)
  +    @max_retries = max_retries
  +    @base_retry_delay = base_retry_delay
  +  end
  - def initialize(builder)
  -    builder = @builder
  -  end

  ```
- And in `example.rb`:

 ```diff
  + client  = Boukensha::Client.new 
  + response = client.call(builder)
  - client  = Boukensha::Client.new(builder)
  - response = client.call
 ```
### 05_agent_loop
- Due to the change in stateless client design implemented in `04_api_client`, we had introduce changes to the `agent.rb`:
 ```diff
  + response = @client.call(@builder, **call_opts)
  - response = @client.call(@builder, **call_opts)
 ```
- Also, we got an error when running the `example.rb`:
```zsh
The Agent Loop is the heart of BOUKENSHA. E
[iteration 2/25]
boukensha/client.rb:63:in 'Boukensha::Client#call': API request failed after 1 attempt (400): { (Boukensha::ApiError)
  "error": {
    "code": 400,
    "message": "Function call is missing a thought_signature in functionCall parts. This is required for tools to work correctly, and missing thought_signature may lead to degraded model performance. Additional data, function call `default_api:read_file` , position 2. Please refer to https://ai.google.dev/gemini-api/docs/thought-signatures for more details.",
    "status": "INVALID_ARGUMENT"
  }
```
- This is becausethe `tool_use` block and the `functionCall` parts were missing the `thought_signature` key so had to add them in `parse_response` and update `assistant_parts`:
```ruby
  sig = part["thoughtSignature"] || part            ["thought_signature"]                                                                                    
  block["thought_signature"] = sig if sig     
```
```ruby
 sig = b["thought_signature"] || b["thoughtSignature"]                                                                                          
  part[:thoughtSignature] = sig if sig  
```
- Also, due to the stateless client architecture, `client.rb` had to be updated:
```ruby
    # rest of code...
    def call(builder, max_output_tokens: 1024, tools: nil)
    # rest of code...
```
- And also `agent.rb`:
```ruby
      def wrap_up(reason)
      @context.add_message(:user, WRAP_UP_DIRECTIVE)
      response = @client.call(@builder, tools: [], max_output_tokens: WRAP_UP_OUTPUT_TOKENS) # the tools: []
```

