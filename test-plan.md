# Chore Board — Test Plan

## 1. Chore Management (ChoreManager)

### 1.1 Create Chore
- [ ] **Positive:** Create a chore with valid title, points, and assigned participant → chore persists with all fields
- [ ] **Positive:** Create a chore with points = 0 → chore created (edge case: zero-value chore)
- [ ] **Positive:** Create a chore with points > 100 → chore created (no upper-bound requirement)
- [ ] **Negative:** Create a chore with missing title → raises error or rejects
- [ ] **Negative:** Create a chore with empty string title → raises error or rejects
- [ ] **Negative:** Create a chore with negative points → raises error or rejects
- [ ] **Negative:** Create a chore with non-integer points (float, string) → raises error or rejects
- [ ] **Negative:** Create a chore for a non-existent participant → raises error or rejects
- [ ] **Error:** ChoreManager initialized with corrupted state → graceful recovery or error

### 1.2 Update Chore
- [ ] **Positive:** Update points of an existing chore → points change, chore persists
- [ ] **Positive:** Update chore title → title changes
- [ ] **Positive:** Update chore assigned participant → assignment changes
- [ ] **Negative:** Update a non-existent chore ID → raises error or no-op with warning
- [ ] **Negative:** Update chore with invalid points (negative, non-integer) → raises error
- [ ] **Negative:** Update chore to assign non-existent participant → raises error

### 1.3 Toggle Chore Active/Inactive
- [ ] **Positive:** Deactivate a chore → chore marked inactive, removed from Todo List sync
- [ ] **Positive:** Reactivate a chore → chore marked active, re-synced to Todo List
- [ ] **Negative:** Toggle non-existent chore → raises error or no-op

### 1.4 Delete Chore
- [ ] **Positive:** Delete a chore → chore removed from storage and Todo List
- [ ] **Negative:** Delete a non-existent chore → raises error or no-op

### 1.5 List/Query Chores
- [ ] **Positive:** List all chores → returns full list
- [ ] **Positive:** List active chores only → excludes inactive chores
- [ ] **Positive:** List chores assigned to a specific participant → filtered correctly
- [ ] **Error:** No chores exist → returns empty list (not None or crash)

---

## 2. Member Management (HA Users)

### 2.1 Add Participant
- [ ] **Positive:** Add HA user as participant → user ID registered, appears in participant list
- [ ] **Positive:** Add HA user with linked external account (e.g., Todoist username) → both stored
- [ ] **Negative:** Add duplicate HA user as participant → rejected (idempotent or error)
- [ ] **Negative:** Add non-existent HA user → raises error or rejected

### 2.2 Remove Participant
- [ ] **Positive:** Remove a participant → removed from list, chores unassigned
- [ ] **Negative:** Remove a participant who has no chore history → succeeds (cleanup)
- [ ] **Negative:** Remove a participant with existing chore assignments → chores redistributed or reassigned

### 2.3 Link External Account
- [ ] **Positive:** Link a Todoist username to a participant → stored and retrievable
- [ ] **Positive:** Update an existing external account link → replaces old value
- [ ] **Positive:** Remove external account link → stored as null/empty
- [ ] **Negative:** Link empty string as external account → rejected or stored as null

### 2.4 Participant Lookup
- [ ] **Positive:** Look up participant by HA user ID → returns correct record
- [ ] **Negative:** Look up non-existent user → returns None or raises specific error
- [ ] **Positive:** Get all participant IDs → returns list of HA user IDs

---

## 3. Scoring (Point Awards & Sensors)

### 3.1 Award Points
- [ ] **Positive:** Award points for a chore to a participant → points added to score, history recorded
- [ ] **Positive:** Award points for an ad-hoc task → logged with custom description
- [ ] **Positive:** Award zero points → no score change, history entry still recorded
- [ ] **Positive:** Award points to a participant not in participant list → rejected or auto-adds
- [ ] **Negative:** Award points for a non-existent chore → raises error
- [ ] **Negative:** Award points with negative value → raises error
- [ ] **Negative:** Award points twice for the same task attribution → prevents double-counting
- [ ] **Error:** Award points when coordinator state is corrupted → graceful error

### 3.2 Score Sensors
- [ ] **Positive:** Sensor reports correct total points for a participant
- [ ] **Positive:** Sensor updates after points are awarded (state reflects latest score)
- [ ] **Positive:** Sensor shows recent activity history in attributes
- [ ] **Positive:** Sensor for a participant with zero points → shows 0
- [ ] **Negative:** Sensor for a removed participant → handled gracefully (removed or shows 0)
- [ ] **Error:** Sensor initialized with no participants → no crash, returns 0

### 3.3 Score History
- [ ] **Positive:** History records timestamp, chore title, points, participant
- [ ] **Positive:** History is append-only (entries never overwritten)
- [ ] **Negative:** History with 1000+ entries → does not crash, queryable
- [ ] **Positive:** History filtered to recent N entries → returns correct subset

---

## 4. Attribution Flow

### 4.1 Pending Attribution Lifecycle
- [ ] **Positive:** Completed task detected → enters "pending attribution" state
- [ ] **Positive:** Attribution resolved → points awarded, pending state cleared
- [ ] **Positive:** Attribution dismissed (acknowledged away) → pending state cleared, no points awarded
- [ ] **Negative:** Acknowledge a non-existent pending attribution → raises error or no-op
- [ ] **Negative:** Attribute a task that was never completed → raises error
- [ ] **Error:** Multiple completions detected simultaneously → each handled independently

### 4.2 Auto-Attribution (Kiosk)
- [ ] **Positive:** Known participant completes task → points awarded immediately, no popup
- [ ] **Positive:** Unknown user completes task → attribution popup shown, manual selection required
- [ ] **Positive:** Known participant selects themselves from popup → points awarded
- [ ] **Negative:** Unknown user completes task, no participant selected → task remains unattributed
- [ ] **Error:** Known participant list empty during auto-attribution → falls back to popup

### 4.3 Coordinator Polling & Completion Detection
- [ ] **Positive:** New task added to Todo List → coordinator detects and creates task item
- [ ] **Positive:** Task completed in Todo List → coordinator detects completion
- [ ] **Positive:** Task deleted from Todo List → coordinator detects removal
- [ ] **Positive:** Task modified (title changed) in Todo List → coordinator detects change
- [ ] **Negative:** Todo List returns empty response → handled gracefully, no crash
- [ ] **Negative:** Todo List service call fails → retry logic or error logged
- [ ] **Error:** HA API unavailable during poll → error handled, doesn't block other operations

---

## 5. LLM Scoring

### 5.1 LLM Configuration
- [ ] **Positive:** Save valid LLM config (base_url, api_key, model) → config persisted
- [ ] **Positive:** Update existing LLM config → values replaced
- [ ] **Positive:** Clear LLM config (remove api_key) → config cleared, fallback behavior active
- [ ] **Negative:** Save config with empty base_url → rejected or default used
- [ ] **Negative:** Save config with invalid URL format → rejected

### 5.2 AI Score Task
- [ ] **Positive:** Score a simple chore description with valid LLM config → returns integer points
- [ ] **Positive:** Score an ad-hoc task description → LLM returns points, task logged
- [ ] **Positive:** Score with LLM returning non-standard response (e.g., 0, 1, 50) → handled
- [ ] **Negative:** Score with no LLM config → falls back to 10 points
- [ ] **Negative:** Score with invalid LLM config (bad key, unreachable URL) → falls back to 10 points
- [ ] **Negative:** Score with LLM returning non-integer response → falls back to 10 points
- [ ] **Negative:** Score with LLM returning negative points → falls back to 10 points
- [ ] **Error:** LLM API returns HTTP 500 → falls back to 10 points, error logged
- [ ] **Error:** LLM API times out → falls back to 10 points, error logged
- [ ] **Error:** LLM API returns malformed JSON → falls back to 10 points, error logged

---

## 6. Services

### 6.1 `chore_board.assign_chore`
- [ ] **Positive:** Assign chore with valid data → chore added to storage and Todo List
- [ ] **Positive:** Assign chore already in Todo List → idempotent (no duplicate)
- [ ] **Negative:** Assign chore with missing required fields → error returned
- [ ] **Negative:** Assign chore with invalid points → error returned
- [ ] **Error:** Todo List service unavailable → error returned, chore still stored

### 6.2 `chore_board.award_points`
- [ ] **Positive:** Award points with valid participant ID and chore ID → points awarded
- [ ] **Negative:** Award points with invalid participant ID → error returned
- [ ] **Negative:** Award points with invalid chore ID → error returned
- [ ] **Negative:** Award points with negative point value → error returned
- [ ] **Error:** Award points when service is called with missing data → error returned

### 6.3 `chore_board.adjust_chore_points`
- [ ] **Positive:** Adjust points up → new points saved
- [ ] **Positive:** Adjust points down → new points saved
- [ ] **Negative:** Adjust points for non-existent chore → error returned
- [ ] **Negative:** Adjust points to invalid value → error returned

### 6.4 `chore_board.log_task`
- [ ] **Positive:** Log task with description and points → task logged, points awarded
- [ ] **Positive:** Log task with auto-attribution (current user is participant) → points awarded immediately
- [ ] **Negative:** Log task with missing description → error returned
- [ ] **Negative:** Log task with invalid points → error returned

### 6.5 `chore_board.ai_score`
- [ ] **Positive:** Score task with LLM → points returned, task logged
- [ ] **Negative:** Score task with no LLM config → falls back to 10 points, logs warning
- [ ] **Error:** Score task with LLM failure → falls back to 10 points, logs error

### 6.6 `chore_board.acknowledge`
- [ ] **Positive:** Acknowledge pending attribution → dismissed, no points awarded
- [ ] **Negative:** Acknowledge non-existent attribution → error returned
- [ ] **Error:** Acknowledge with invalid data → error returned

---

## 7. Kiosk Card

### 7.1 Display
- [ ] **Positive:** Load kiosk card as known participant → shows user's name in header
- [ ] **Positive:** Load kiosk card as unknown user → shows "Who completed this?" prompt
- [ ] **Positive:** Load kiosk card as admin → shows admin panel access
- [ ] **Positive:** Load kiosk card with no pending chores → shows empty state
- [ ] **Negative:** Load kiosk card with no HA user context → shows error or default state
- [ ] **Error:** Load kiosk card with corrupted chore data → graceful error display

### 7.2 Task Completion
- [ ] **Positive:** Click ✓ on a chore as known participant → task completed, points awarded, list refreshes
- [ ] **Positive:** Click ✓ on a chore as unknown user → attribution popup opens
- [ ] **Positive:** Select participant from attribution popup → points awarded to selected user
- [ ] **Negative:** Click ✓ on a chore that was already completed → no double-award
- [ ] **Error:** Click ✓ when HA API is unavailable → error toast, task remains incomplete

### 7.3 Leaderboard Display
- [ ] **Positive:** Show leaderboard when user is a participant → all participant scores displayed
- [ ] **Positive:** Leaderboard sorted by score (descending)
- [ ] **Positive:** Leaderboard shows recent activity per participant
- [ ] **Negative:** Show leaderboard with only one participant → displays correctly
- [ ] **Error:** Leaderboard data unavailable → shows loading or error state

### 7.4 Refresh
- [ ] **Positive:** Configurable refresh interval works → data updates at specified interval
- [ ] **Positive:** Manual refresh triggered → data updates immediately
- [ ] **Negative:** Refresh interval set to 0 → handled (no refresh or immediate error)

---

## 8. Admin Panel

### 8.1 Chores Tab
- [ ] **Positive:** Edit points for a chore → changes saved and reflected in Todo List sync
- [ ] **Positive:** Toggle chore active/inactive → chore state updated
- [ ] **Negative:** Edit points to invalid value → validation error shown
- [ ] **Error:** Admin panel cannot read chore data → error state displayed

### 8.2 Participants Tab
- [ ] **Positive:** Select HA users as participants → user list populates, selection saves
- [ ] **Positive:** Link external account to participant → saved and displayed
- [ ] **Positive:** Remove a participant → removed from list and chore assignments
- [ ] **Negative:** Select non-existent HA user → rejected
- [ ] **Error:** HA user list unavailable → error state displayed

### 8.3 LLM Config Tab
- [ ] **Positive:** Save valid LLM config → config saved, test indicator shows success
- [ ] **Positive:** Test LLM connection → validates base_url, api_key, and model
- [ ] **Positive:** Clear LLM config → removed, fallback active
- [ ] **Negative:** Save LLM config with invalid URL → validation error
- [ ] **Negative:** Save LLM config with invalid API key → validation or test fails
- [ ] **Error:** LLM test request fails → error message shown

### 8.4 Admin Access Control
- [ ] **Positive:** Admin user can access admin panel → panel loads
- [ ] **Negative:** Non-admin user tries to access admin panel → access denied or panel hidden
- [ ] **Error:** Admin panel loads with no admin user detected → error or redirect

---

## 9. Todo Store (HATodoStore)

### 9.1 Initialize
- [ ] **Positive:** Initialize with valid HA config → store ready
- [ ] **Negative:** Initialize with invalid HA config → error, store not usable
- [ ] **Error:** Initialize when HA is unavailable → error handled gracefully

### 9.2 Poll
- [ ] **Positive:** Poll returns new tasks → detected and reported
- [ ] **Positive:** Poll returns no changes → no false positives
- [ ] **Positive:** Poll returns completed tasks → detected as completions
- [ ] **Positive:** Poll returns deleted tasks → detected as deletions
- [ ] **Negative:** Poll returns malformed data → handled gracefully
- [ ] **Error:** Poll times out → retry or error logged
- [ ] **Error:** HA API returns 4xx/5xx → error logged, doesn't crash

### 9.3 Sync with Chores
- [ ] **Positive:** Sync chore list to Todo List → tasks match chore definitions
- [ ] **Positive:** Remove chore from Todo List when deactivated → task removed
- [ ] **Negative:** Sync with empty chore list → Todo List cleared of chore tasks
- [ ] **Error:** Sync fails mid-operation → partial state handled, no corruption

---

## 10. Persistence & State

### 10.1 Storage
- [ ] **Positive:** All data survives restart (chores, participants, scores, LLM config)
- [ ] **Positive:** Corrupted storage file → graceful recovery or fresh start
- [ ] **Negative:** Storage disk full → error logged, no crash
- [ ] **Error:** Storage write fails → error logged, in-memory state preserved

### 10.2 Baseline Persistence (`_seen_uids`)
- [ ] **Positive:** Seen UIDs persist across restarts → no false "new task" reports after restart
- [ ] **Negative:** `_seen_uids` not persisted → first poll after restart reports all tasks as new (known issue)
- [ ] **Error:** `_seen_uids` corrupted → reset to empty set

---

## 11. Edge Cases & Integration

### 11.1 Concurrent Operations
- [ ] **Positive:** Multiple users complete tasks simultaneously → all attributed correctly
- [ ] **Positive:** Admin edits chore while coordinator is polling → no data corruption
- [ ] **Error:** Concurrent writes to storage → handled by HA storage layer

### 11.2 Large Scale
- [ ] **Positive:** 100+ chores defined → system handles without performance issues
- [ ] **Positive:** 50+ participants → leaderboard and sensors function correctly
- [ ] **Positive:** 10,000+ history entries → queryable, sensors still performant

### 11.3 Integration with HA
- [ ] **Positive:** Integration loads in HA without errors
- [ ] **Positive:** Sensors appear in HA state machine with correct entity IDs
- [ ] **Positive:** Services callable from HA automation/script
- [ ] **Negative:** HA version incompatible → graceful error at setup
- [ ] **Error:** HA restarts during polling → coordinator reinitializes correctly

### 11.4 WebSocket (Admin Panel Communication)
- [ ] **Positive:** WebSocket commands from admin panel reach backend
- [ ] **Positive:** State changes pushed to admin panel via WebSocket
- [ ] **Negative:** WebSocket connection drops → reconnection or error handled
- [ ] **Error:** Invalid WebSocket command → error returned
