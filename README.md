# Chore Board

Gamified household chore tracker using HA's built-in Todo List as source of truth.

## Features

- **HA Todo List integration** — manage chores in HA's native Todo Lists UI
- **Member management** — define household members with HA user + Todoist accounts
- **Chore points** — assign point values to chores
- **Leaderboard** — per-member score sensors
- **Kiosk card** — custom Lovelace card for task completion with attribution
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

### 1. Create a Todo List

Use HA's built-in Todo List (Settings → Devices & Services → Todo Lists) or any backend.

### 2. Add Chore Board Integration

1. Add the integration via **Settings → Devices & Services → Add Integration**
2. Select your Todo List entity
3. Define members as JSON:
   ```json
   [
     {"id": "josh", "name": "Josh", "ha_user_id": "abc123", "todoist_username": "josh"},
     {"id": "sarah", "name": "Sarah", "ha_user_id": "def456", "todoist_username": "sarah"}
   ]
   ```

### 3. Install the Kiosk Card

Build the card:
```bash
cd homeassistant/custom_components/chore_board/kiosk-card
npm install
npm run build
```

Copy the built card to your HA config:
```bash
mkdir -p ~/.homeassistant/www/custom-lovelace
cp dist/chore-board-card.js ~/.homeassistant/www/custom-lovelace/
```

Add to Lovelace resources (Configuration → Lovelace Dashboards → Resources):
```yaml
url: /local/custom-lovelace/chore-board-card.js
type: module
```

### 4. Add Chores

Via service call:
```yaml
service: chore_board.assign_chore
data:
  chore_id: chore_dishes
  title: Wash the dishes
  points: 10
```

## Services

- `chore_board.assign_chore` — add a chore to the Todo List
- `chore_board.award_points` — attribute a completed task to a member
- `chore_board.log_task` — log an ad-hoc "I did a thing"
- `chore_board.ai_score` — use LLM to score an unlisted task
- `chore_board.acknowledge` — dismiss a pending attribution request

## Kiosk Card Usage

Add to a Lovelace dashboard:
```yaml
type: custom:chore-board-card
entity: todo.chore_list
title: Household Chores
refresh_interval: 30
```

The card shows:
- Current HA user's name
- All pending chores
- ✓ button to complete tasks
- Popup if user is not a known member (asks who completed it)

## Automation: Auto-attribute on kiosk completion

The kiosk card handles attribution automatically. For voice/other completions, use:

```yaml
alias: "Chore Board - detect completion"
trigger:
  - platform: event
    event_type: todo.item_completed
action:
  - service: todo.get_items
    data:
      entity_id: todo.chore_list
    response_variable: completed
  # Then use award_points service with the member who did it
```
