"""Constants for Chore Board."""

DOMAIN = "chore_board"

# Store types
STORE_LOCAL = "local"
STORE_TODOIST = "todoist"
VALID_STORE_TYPES = {STORE_LOCAL, STORE_TODOIST}

# Service names
SERVICE_ASSIGN_CHORE = "assign_chore"
SERVICE_COMPLETE = "complete"
SERVICE_LOG_TASK = "log_task"
SERVICE_AI_SCORE = "ai_score"

# Storage keys
STORAGE_KEY = f"{DOMAIN}.storage"
STORAGE_VERSION = 1

# Default LLM model
DEFAULT_LLM_MODEL = "gpt-4o-mini"

# Point defaults
DEFAULT_POINTS = 10
