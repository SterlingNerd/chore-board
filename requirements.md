# Chore Board — Requirements

## Overview

Gamified household chore tracker using HA's built-in Todo List as source of truth. Home Assistant is the scoring/attribution layer — tasks are managed in HA's native Todo Lists UI.

---

## Core Requirements

### Task Management
- Tasks live in HA's built-in Todo List (any backend: Local to-do, Shopping List, etc.)
- HA polls for changes: new tasks, completions, deletions
- Tasks managed in HA's native Todo Lists dashboard or via service calls
- Chores synced from HA to the Todo List

### Participants = HA Users
- Participants are Home Assistant user accounts — no separate identity system
- Configured by selecting HA users in the integration setup
- Each participant can optionally link an **external account** (e.g., Todoist username) for future task sync
- The HA user ID is the sole identifier — no `member_id` or separate names

### Chore Points
- Each chore has a configurable point value
- Points adjustable per chore (for correcting auto-weighting mistakes)
- Points persisted in HA storage

### Leaderboard
- Per-participant score sensors visible in HA dashboard
- Also displayed in the kiosk card when the current user is a participant
- Shows recent activity history per participant

### Kiosk Card
- Custom Lovelace card for task completion on a kiosk display
- Shows current HA user's name in header
- Lists pending chores with completion buttons
- **Auto-attribution**: if the current user is a known participant, points are awarded immediately
- **Popup for unknown users**: "Who completed this?" with participant selection buttons
- Displays leaderboard when the current user is a participant
- Configurable refresh interval

### Admin Panel
- Custom Lovelace panel (admin-only) with three tabs:
  - **Chores**: edit point values for each chore
  - **Participants**: select HA users, link external accounts
  - **LLM Config**: configure base URL, API key, model for scoring

### LLM Scoring
- Configurable OpenAI-compatible API (base URL, API key, model)
- Used to score ad-hoc tasks that weren't on the chore list
- Falls back to 10 points on failure
- Any OpenAI-compatible endpoint works (not just OpenAI)

### "I Did a Thing" — Ad-hoc Task Logging
- Manual service to log an ad-hoc task and award points
- LLM-powered scoring service for unlisted tasks

### Attribution Flow
- HA polls the Todo List and detects completions
- Completed tasks enter a "pending attribution" state
- Kiosk card resolves attribution automatically for known participants
- Manual resolution via service call or dismiss button for edge cases

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

## Out of Scope

- **Voice integration** — explicitly excluded by user

---

## Future Possibilities

- Streaks / bonus points for consistency
- Chore templates library
- Notification integration on completion
- Per-member stats and completion rates
