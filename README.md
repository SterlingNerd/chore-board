# Chore Board

Gamified household chore tracker with a configurable todo store backend and Home Assistant integration.

## Features

- **Configurable stores** — local (default) or Todoist
- **Member management** — define household members with names and avatars
- **Chore points** — assign point values to chores
- **"I did a thing"** — log ad-hoc tasks, optionally AI-scored
- **Home Assistant native** — sensors, services, voice assistant ready

## Installation (HACS)

1. Open HACS in Home Assistant
2. Go to **Integrations** → **Explore & Add Repositories**
3. Search for "Chore Board" or add this repository:
   ```
   https://github.com/josh/chore-board
   ```
4. Install and restart Home Assistant
5. Add the integration via **Settings → Devices & Services → Add Integration**

## Manual Installation

Copy the `homeassistant/custom_components/chore_board` directory to your HA config's `custom_components/` directory:

```bash
mkdir -p ~/.homeassistant/custom_components/
cp -r homeassistant/custom_components/chore_board ~/.homeassistant/custom_components/
```

Restart Home Assistant.

## Configuration

```yaml
# Example: via UI after adding the integration
# - Select store type (local or todoist)
# - Provide Todoist token if using Todoist
# - Add members as JSON: [{"id": "josh", "name": "Josh"}, {"id": "sarah", "name": "Sarah"}]
```

## Services

- `chore_board.assign_chore` — add a chore to the board
- `chore_board.award_points` — attribute a completed task to a member
- `chore_board.log_task` — log an ad-hoc "I did a thing"
- `chore_board.ai_score` — use LLM to score an unlisted task
- `chore_board.acknowledge` — dismiss a pending attribution request
