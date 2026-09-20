# Chore Board — Architecture

Gamified household chore tracker using HA's built-in Todo List as source of truth.

## Design Principles

- **HA Todo List is the single source of truth** for tasks. HA is the scoring/attribution layer.
- **Members = HA users.** No separate identity system. Each participant is an HA user account.
- **External accounts are optional.** Members can optionally link a Todoist (or other) username.
- **Kiosk card handles attribution.** If the current user is a known participant, points are awarded immediately. If not, a popup asks "who did this?"
- **Leaderboard in kiosk.** The kiosk card shows the leaderboard when the current user is a participant.

## Components

### Backend (Python)

```
chore_board/
├── __init__.py              # Thin entry point. Delegates to subsystems.
├── chore.py                 # Chore dataclass + ChoreManager (CRUD)
├── member.py                # HA user → participant lookup
├── scoring.py               # LLMConfig + ai_score_task (OpenAI-compatible)
├── coordinator.py           # Polling + state management only
├── attribution.py           # Pending attribution lifecycle
├── sensor.py                # Per-participant score sensors
├── services/                # One module per service handler
│   ├── chore_handlers.py
│   ├── scoring_handlers.py
│   └── member_handlers.py
├── websocket.py             # WS commands for admin panel
├── todo_store/
│   ├── base.py              # ABC: initialize, poll, list
│   └── ha_todos.py          # HA Todo List adapter
├── admin-panel/             # Build → chore-board-admin.js
└── kiosk-card/              # Build → chore-board-card.js
```

### Frontend (TypeScript / Lit)

- **Kiosk card** — task list, completion buttons, attribution popup, leaderboard
- **Admin panel** — chores tab, participants tab, LLM config tab (admin-only)

## Data Flow

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

1. Tasks live in HA Todo List (any backend)
2. Coordinator polls → detects completions via delta comparison
3. Kiosk card attributes to HA user → awards points
4. Sensors update leaderboard
5. Admin panel manages everything (chores, participants, LLM config)

## Planned Improvements

### 1. Separate `sync_with_chores` from `TodoStore` ABC

Currently the ABC has `sync_with_chores(chores_data)`. A storage adapter shouldn't know about chore definitions — that's the coordinator's job. Move chore-to-store syncing into the coordinator or a separate sync service. The ABC should just be: `initialize`, `poll`, `list`.

### 2. Fix `_seen_uids` baseline persistence

`HATodoStore._seen_uids` is a plain set — restarts lose the baseline, so the first poll after restart reports everything as new. Persist the last-seen UID set to HA storage or the config entry.

### 3. Break up the coordinator

The coordinator handles: polling, completion detection, attribution, scoring, point awards, chore point adjustment, LLM config, history management. Split into:
- `ChoreBoardCoordinator` — polling + state management
- `AttributionService` — pending attribution lifecycle
- `ScoringService` — point calculation + logging

### 4. Extract service handlers

Each service handler is currently an inline `async def` inside `async_setup_services`. Extract each to its own function (one module per handler group). This makes testing possible.

### 5. Add tests

The coordinator, chore manager, scoring, and store all have pure logic that can be unit-tested in isolation:
- `test_chore.py` — ChoreManager CRUD
- `test_scoring.py` — ai_score_task (mock openai)
- `test_coordinator.py` — attribution flow
- `test_attribution.py` — pending attribution lifecycle

### 6. Remove dead factory

`factory.py` only ever creates `HATodoStore`. Either remove it or make it actually useful.

### 7. Sensor history filtering

`sensor.py` filters full history with a list comprehension on every read. Filter at the source or cache the result.

### 8. Websocket module

`websocket.py` currently has `async_register_websocket` defined as async but called without await — it's a no-op. Fix or simplify.

## Services

| Service | Purpose |
|---------|---------|
| `chore_board.assign_chore` | Add chore to Todo List |
| `chore_board.award_points` | Attribute completed task to participant |
| `chore_board.adjust_chore_points` | Change points for a chore |
| `chore_board.log_task` | Log ad-hoc task with points |
| `chore_board.ai_score` | LLM-score ad-hoc task, then log |
| `chore_board.acknowledge` | Dismiss pending attribution |

## Out of Scope

- Voice integration (user explicitly excluded)

## Future Possibilities

- Streaks / bonus points for consistency
- Chore templates library
- Notification integration on completion
- Per-member stats and completion rates
