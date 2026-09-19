/**
 * Types for Chore Board Kiosk Card
 */

export interface TodoItem {
  uid: string;
  summary: string;
  status: "needs_action" | "completed";
  due?: string;
  description?: string;
}

export interface ChoreBoardCardConfig {
  type: string;
  entity: string;
  title?: string;
  refresh_interval?: number;
}

export interface MemberInfo {
  id: string;
  name: string;
  ha_user_id?: string;
  todoist_username?: string;
  avatar?: string;
}
