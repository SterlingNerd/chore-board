# Chore Board

Gamified household chore tracker using HA's built-in Todo List as source of truth.

## Features

- **HA Todo List integration** — manage chores in HA's native Todo Lists UI
- **Member management** — define household members with names and avatars
- **Chore points** — assign point values to chores
- **Leaderboard** — per-member score sensors
- **"I did a thing"** — log ad-hoc tasks, optionally AI-scored
- **Voice assistant ready** — triggers on todo.item_completed

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

Copy the `homeassistant/custom_components/chore_board` directory to your HA config's `custom_components/` directory.

## Setup

1. **Create a Todo List** in HA (Settings → Devices & Services → Todo Lists)
   - Use any backend: Local to-do, Shopping List, etc.
2. **Add Chore Board integration** and select your Todo List
3. **Define members** as JSON:
   ```json
   [{"id": "josh", "name": "Josh"}, {"id": "sarah", "name": "Sarah"}]
   ```
4. **Add chores** via the `chore_board.assign_chore` service

## Services

- `chore_board.assign_chore` — add a chore to the Todo List
- `chore_board.award_points` — attribute a completed task to a member
- `chore_board.log_task` — log an ad-hoc "I did a thing"
- `chore_board.ai_score` — use LLM to score an unlisted task
- `chore_board.acknowledge` — dismiss a pending attribution request

## Automation: Auto-attribute on completion

```yaml
alias: "Chore Board - detect completion"
trigger:
  - platform: event
    event_type: todo.item_completed
action:
  - service: todo.get_items
    data:
      entity_id: todo.your_list
    response_variable: completed
  # Then use award_points service with the member who did it
```
