# Chore Board

Gamified household chore tracker with a configurable todo store backend and Home Assistant integration.

## Features

- **Configurable stores** — local (default) or Todoist
- **Member management** — define household members with names and avatars
- **Chore points** — assign point values to chores
- **"I did a thing"** — log ad-hoc tasks, optionally AI-scored
- **Home Assistant native** — sensors, services, voice assistant ready

## Installation

Copy `homeassistant/custom_components/chore_board` to your HA config's `custom_components/` directory.

## Configuration

```yaml
chore_board:
  members:
    - id: josh
      name: Josh
    - id: sarah
      name: Sarah

  store:
    type: local  # or "todoist"

  # optional: todoist credentials
  # todoist:
  #   token: !secret todoist_token
```

## Services

- `chore_board.assign_chore` — add a chore to the board
- `chore_board.complete` — mark a chore done, award points
- `chore_board.log_task` — log an ad-hoc "I did a thing"
- `chore_board.ai_score` — use LLM to score an unlisted task
