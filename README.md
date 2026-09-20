# Chore Board

Gamified household chore tracker using HA's built-in Todo List as source of truth. Home Assistant is the scoring/attribution layer — tasks are managed in HA's native Todo Lists UI.

---

## Completed Features

### 1. Task Source of Truth — HA Todo List
- Uses `todo.get_items`, `todo.add_item`, `todo.remove_item` services
- Polls for changes (new tasks, completions, deletions)
- Backend-agnostic: works with any HA Todo List integration
- Tasks managed in HA's native Todo Lists dashboard or via services

### 2. Members = HA Users
- Members are Home Assistant user accounts — no separate IDs or names
- Configured by selecting HA users in the config flow
- Each member can optionally link an **external account** (e.g., Todoist username) for future task sync
- No `member_id` field — the HA user ID is the identifier

### 3. Chore Management
- Chores defined with: `id`, `title`, `points`, `assigned_to`, `active`
- Synced to HA Todo List via `assign_chore` service
- Points adjustable per chore (for correcting auto-weighting mistakes)
- Persisted in HA storage

### 4. Leaderboard
- Per-member `sensor.chore_board_{member}_score` entities
- Shows total points in HA dashboard
- Attributes include recent activity history
- **Kiosk card also displays leaderboard** — customized view if current user is a participant

### 5. Kiosk Card (`custom:chore-board-card`)
- Shows current HA user's name in header
- Lists pending chores with ✓ completion buttons
- **Auto-attribution**: if user is a known participant, points awarded immediately
- **Popup for unknown users**: "Who completed this?" with participant selection buttons
- Displays leaderboard if current user is a participant
- Configurable refresh interval

### 6. Admin Panel (`custom:chore-board-admin`, admin-only)
- **Chores tab**: edit points for each chore
- **Participants tab**: select HA users, link external accounts (Todoist, etc.)
- **LLM Config tab**: configure base URL, API key, model

### 7. LLM Scoring (Configurable)
- `LLMConfig` with `base_url`, `api_key`, `model`
- OpenAI-compatible API (works with any chat completions endpoint)
- Falls back to 10 points on failure
- Used by `ai_score` service for ad-hoc task scoring

### 8. "I Did a Thing" — Ad-hoc Task Logging
- `log_task` service: manually log a task and award points
- `ai_score` service: LLM scores an unlisted task description, then logs it

### 9. Attribution Flow
- Coordinator polls todo store for completions
- Completed tasks go into "pending attribution" state
- `award_points` service: attribute a task to a participant (HA user)
- `acknowledge` service: dismiss a pending attribution
- Kiosk card handles attribution automatically when user is a known participant

---

## Services

| Service | Purpose |
|---------|---------|
| `chore_board.assign_chore` | Add chore to Todo List |
| `chore_board.award_points` | Attribute completed task to participant |
| `chore_board.adjust_chore_points` | Change points for a chore |
| `chore_board.log_task` | Log ad-hoc task with points |
| `chore_board.ai_score` | LLM-score ad-hoc task, then log |
| `chore_board.acknowledge` | Dismiss pending attribution |

---

## Planned / Out of Scope

### Voice Integration — **Out of Scope**
User explicitly excluded this. Would have involved conversation intents for "Josh did the dishes" style commands.

### What's Next (If Desired)

1. **Build the cards** — `npm install && npm run build` in kiosk-card/ and admin-panel/
2. **Lovelace dashboard recipe** — pre-built dashboard YAML with kiosk + leaderboard + admin
3. **Streaks / bonuses** — daily/weekly bonus points for consistency
4. **Chore templates** — predefined chore library users can add
5. **Additional store backends** — if users want other Todo List backends
6. **Notification integration** — push notifications when tasks are completed
7. **History/reports** — per-member stats, completion rates, etc.

---

## Architecture

```
HA Todo List ←→ HATodoStore (polls get_items)
                    ↓
            ChoreBoardCoordinator
                    ↓
    ┌───────────────┼───────────────┐
    ↓               ↓               ↓
Score Sensors   Kiosk Card     Admin Panel
(leaderboard)   (attribution  (chore/participant/LLM)
                + leaderboard)
```

**Data flow:**
1. Tasks live in HA Todo List (any backend)
2. Coordinator polls → detects completions
3. Kiosk card attributes to HA user → awards points
4. Sensors update leaderboard
5. Admin panel manages everything (chores, participants, LLM config)

**Participants = HA Users:**
- Selected by HA user ID in config
- Optionally linked to external accounts (Todoist, etc.)
- Used for kiosk attribution and leaderboard display
