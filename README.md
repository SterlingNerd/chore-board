# Chore Board

Gamified household chore tracker using HA's built-in Todo List as source of truth.

## Features

- **HA Todo List integration** — manage chores in HA's native Todo Lists UI
- **Member management** — define household members with HA user + Todoist accounts
- **Chore points** — assign point values to chores, adjustable per chore
- **Leaderboard** — per-member score sensors
- **Kiosk card** — custom Lovelace card for task completion with attribution
- **Admin panel** — manage chores, members, and LLM config (admin only)
- **"I did a thing"** — log ad-hoc tasks, optionally AI-scored
- **Configurable LLM** — OpenAI-compatible API with fallback

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
3. Configure LLM (optional): base URL, API key, model
4. Define members as JSON:
   ```json
   [
     {"id": "josh", "name": "Josh", "ha_user_id": "abc123", "todoist_username": "josh"},
     {"id": "sarah", "name": "Sarah", "ha_user_id": "def456", "todoist_username": "sarah"}
   ]
   ```

### 3. Install the Cards

Build the cards:
```bash
cd homeassistant/custom_components/chore_board/kiosk-card
npm install && npm run build

cd ../admin-panel
npm install && npm run build
```

Copy to your HA config:
```bash
mkdir -p ~/.homeassistant/www/custom-lovelace
cp kiosk-card/dist/chore-board-card.js admin-panel/dist/chore-board-admin.js ~/.homeassistant/www/custom-lovelace/
```

Add to Lovelace resources (Configuration → Lovelace Dashboards → Resources):
```yaml
url: /local/custom-lovelace/chore-board-card.js
type: module
url: /local/custom-lovelace/chore-board-admin.js
type: module
```

### 4. Add the Admin Panel

Add to a dashboard (HA admin only):
```yaml
type: custom:chore-board-admin
```

### 5. Add Chores

Via service call:
```yaml
service: chore_board.assign_chore
data:
  chore_id: chore_dishes
  title: Wash the dishes
  points: 10
```

## Admin Panel

The admin panel (admin-only) provides:

- **Chores tab**: Edit points for each chore
- **Members tab**: Link HA users and Todoist accounts
- **LLM Config tab**: Configure OpenAI-compatible API (base_url, api_key, model)

## Services

- `chore_board.assign_chore` — add a chore to the Todo List
- `chore_board.award_points` — attribute a completed task to a member
- `chore_board.adjust_chore_points` — change points for a chore
- `chore_board.update_member` — update member links (HA user, Todoist)
- `chore_board.update_llm_config` — update LLM configuration
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

## LLM Configuration

Configure in the admin panel or via config flow:

- **Base URL**: OpenAI-compatible API endpoint (e.g., `https://api.openai.com/v1`)
- **API Key**: Your API key
- **Model**: Model name (e.g., `gpt-4o-mini`)

Fallback: If the LLM call fails, scoring defaults to 10 points.

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
