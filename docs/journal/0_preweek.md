## Agent Architecture Exploration

## 1. An agent file with referenced files i.e. GEMINI.md, @~/docs/\*.md

The simplest architecture exploration is creating an agent file e.g. `GEMINI.md` or whichever coding harness is used and then importing other files if needed

We should attempt to create an agent file and check if it can connect to the MUD and complete a simple goal e.g. 'Find the bakery and list items on the menu'

We should use the smallest model or lower thinking effort and then scale up. P.S. for gemini, thinking effort low creates an unusable agent which is unable to persist focus on task

### Technical Observations:

Using Gemini Flash 3.5 thinking effort medium, we created a GEMINI.md with a simple prompt and told that it will need to manager its own local memory via simple markdown files. We provided it location of the MUD and player credentials.

- At thinking level medium, the agent created python scripts to create socket connection and execute commands though it wasn't perfect and it could not persist the socket connection

- At thinking level high, the agent adjusted the python scripts for socket connection to persist in the same shell session and then created a find_path.py script to find shortest path and used a python script to play the game:

```sh
   I have successfully executed the instructions from your GEMINI.md:

   1. Found Route: Calculated the shortest path from The Temple of Midgaard (vnum 3001) to The Bakery (vnum 3009):
      - Go south to The Temple Square (vnum 3005)
      - Go south to Market Square (vnum 3014)
      - Go west to Main Street (vnum 3013)
      - Go north to The Bakery (vnum 3009)

   2. Automated the Agent: Created and ran run_agent.py to:
      - Log into the MUD game as dummy / helloworld.
      - Send the step-by-step movement directions to reach the Bakery.
      - Execute the list command to extract the menu.

   3. Retrieved Menu:
      - A danish pastry — 7 coins (Unlimited)
      - A bread — 14 coins (Unlimited)
      - A waybread — 72 coins (Unlimited)

   4. Updated State: Saved all the results into data/player.md and data/world.md as instructed.
```

### Technical Conclusion

- We could have created a login script which gives enough context so that the agent did not waste tokens trying to figure out the text user interface. The login flows are deterministic so agent trying to develop a login method consumes tokens unnecessarily

- The agent read the game infrastructure files and then gave me the answer. It did not actually play the game. It was unable to understand instructions properly at medium thinking level

- The agent needed actual commands and instructions in the gemini cli session to properly telnet to the tbaMUD server and play the game. A MUD Manager would help small models to login to the game server. It had no idea about the text user interface to login and see its mistakes

- The agent went off task when it failed to login and instead looked at infrastructure files to create a shortest path algorithm to complete the goal. At this architecture, coding harnesses are not a good fit

- Having an MCP server to the MUD SDK would be much better for this architecture as then the agent can be steered with better context

- Due to complexity of the state data, just updating markdowns is not sufficient

> Use coding harness for coding/specialized task and for special purposes, use own agentic loop

## 2. Agent skills driven by main agent e.g. ~/.skills

A common way to drive agent functionality is by using Agent Skills - an open format adopted by coding harnesses and agent SDKs.

We should create a skill that has its own script that can connect to the MUD and we should attempt to have it play its own game

### Technical Observations

- We used the Anti Gravity CLI with model Gemini 3.5-Flash and skill-creator skill to create a skill to play the MUD game

- The agent attempted to read outside the workspace and I denied the tool call. I had to reprompt the creation of the skill and it created it.

- The agent created a skill `tbamud-player` and created a `mud_client.py` script It changed its code for handling welcome screen message and re-launched commands for exits and evaluating surroundings from the mud client script.

- The agent created reference guides for gameplay and for commands.

- The agent took significantly less time to acheive the objective compared to the plain agent architecture for simple goals. It was able to acheive the goal and it did stop when a task was not possible e.g. when we asked it to practice kick at the swordsmen guild, it was able to find the guild but could not practice as there were no sessions and it reported back. But it never considered if it should attempt to level up or how hard the would it be to level up the kick

- When giving it a harder goal like defeating the minotaur in the newbie zone, it did find the minotaur's location but engaged in combat early without leveling up. Also, it kept brute forcing around the location to maybe avoid the minotaur but at times, it kept attacking the minotaur at every other iteration. It used python scripts to use the MUD client to play the game

- It did update the player and world md files with the player and world state but not in real time. I had to prompt it to add the findings in the right .md files

- A real player would have held the goal and progressed more deliberately, exploring locations and levelling up rather than ending up facing the minotaur prematurely. There is no real time reasoning before it acts in the game.

- If Anti-Gravity's agentic loops change, then the reasoning might break in unexpected ways

- We may need adaptive task management i.e. a way for the agent to update its task as and when it completes. Interestingly, the agent did output a phased campaign plan but there were no tasks and it didn't follow that plan through
  E.g. Goal : Defeat the Massive Minotaur in the Newbie Zone north of town

Before I find the newbie zone, do I need to prepare?

- collect info from NPCs for my goal?
- obtain equipment / inventory ?
- practice / level up?

I head to Newbie zone.

- While on path do I find something that needs a detour? Will this start a sidequest?
- Explorer mode:
  - Focused: Only campaign goals
  - Curios: Consider side quests while on main quest to get additional XP
  - Aloof: Do all sidequests and don't bother about the main quest

I found the Newbie zone.

- Risk mode:
  - Bold: Try and push exploration to end goal and try to engage high level mobs or try and fight stronger opponents
  - Scared: Don't progress exploration unless I am completely healed. Always have plenty of resources if you lose money or if you are hungry/thirsty

### Technical Conclusions

Agent skills definitely work for smaller goals. Though it's a marginal improvement over the referenced file approach, it gives the agent tools to acheive a goal rather than a blank slate approach of goal definition --> outcome. This approach has a better agent steering capability than the referenced agent appproach. Also, it did not keep creating blanket python files at every single iteration. It created scripts when the skill was created and it updated the script when it was necessary

We should define a player persona which describes how the player likes to play based on risk mode, exploration mode.

When we enter a goal, we should see a concrete goal decomposition plan that outlines steps the agent must take to level up accoding to the goal.

## 3a. Agent skills driven by subagent sdk

Subagent SDK is a way for the coding harness to utilize a sub-agent to perform tasks and gets the output as a result of tool calls

We should reuse the skill used in type 2 architecture for the agent to drive the sub-agent to accomplish user goals

### Technical observations

- The agent kept asking for permissions for every python script it tried to run in the local directory. After asking the agent to update permissions, it started updating the global settings

- The agent ended up creating a allow_python script which did not run smoothly on every iteration. Partially because agy cli has an explicit permissions module which overrides any scripting

- The agent spawned the subagent that we created and was able to give it context. The subagent overwrote information from state memory but the orchestrator was able to steer the sub agent and reverted unwanted changes

- The agent spawned two subagents and played the MUD game as two different players. We prompted it to maintain a shared world state memory and individual player state memory. It correctly identified race conditions for the single player state
