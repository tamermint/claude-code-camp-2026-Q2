## Setup

- After building the files with docker, telnet/nc refused to connect:

```zsh
telnet localhost 4000
Trying ::1...
telnet: connect to address ::1: Connection refused
Trying 127.0.0.1...
telnet: connect to address 127.0.0.1: Connection refused
telnet: Unable to connect to remote host
```

- In the docker logs:

```zsh
circlemud  | Using file descriptor for logging.
circlemud exited with code 1 (restarting)
circlemud  | /usr/local/bin/docker-entrypoint.sh: 5: [!: not found
...
```

- Issue was in the docker-entrypoint.sh :

```zsh
if [
```

## Gameplay

- TUI based game do not have an understanding of relative nearness i.e. at the start, the banner mentiones.."An automatic teller machine has been installed in the wall here" but are we close to the wall or close to the paintings on the wall?
