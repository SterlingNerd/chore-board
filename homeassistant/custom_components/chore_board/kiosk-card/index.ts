/**
 * Chore Board Kiosk Card Entry Point
 *
 * This file is the entry point for the custom card.
 * It should be bundled with a tool like rollup or esbuild.
 *
 * Usage in Lovelace:
 * ```yaml
 * type: custom:chore-board-card
 * entity: todo.chore_list
 * title: Household Chores
 * refresh_interval: 30
 * ```
 */

export { ChoreBoardCard } from "./chore-board-card";
export type { ChoreBoardCardConfig, MemberInfo, TodoItem } from "./types";
