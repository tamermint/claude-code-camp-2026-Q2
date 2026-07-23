# The Boukensha Agent

- As part of Exampro's bootcamp, this project is about a player journey agent that explores the gameplay of tbaMUD.

## Setup

- tbaMUD was downloaded from [tbaMUD's official repository](`https://github.com/tbamud/tbamud.git`) and was unpacked to a debian image run on a docker container

- Install dependencies:

  ```zsh
      pnpm -i
  ```

- Install docker (from the official website)

## Start

- To start the container:
  ```zsh
      docker compose up --build
  ```
- Telnet or nc to port 4000
  ```zsh
      telnet localhost 4000
  ```
