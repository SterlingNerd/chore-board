/**
 * Chore Board Kiosk Card
 *
 * Shows the HA Todo List with attribution for task completions.
 * If the current HA user is not a known member, shows a popup.
 */

import {
  css,
  html,
  LitElement,
  nothing,
  TemplateResult,
} from "lit";
import { customElement, property, state } from "lit/decorators.js";
import { HomeAssistant, LovelaceCard } from "custom-card-helpers";
import { TodoItem } from "./types";

// Card configuration
export interface ChoreBoardCardConfig {
  type: string;
  entity: string;          // todo entity
  title?: string;
  refresh_interval?: number; // seconds
}

@customElement("chore-board-card")
export class ChoreBoardCard extends LitElement implements LovelaceCard {
  public static async getConfigElement() {
    const el = document.createElement("chore-board-card-editor");
    await el.updateComplete;
    return el;
  }

  public static getStubConfig() {
    return { type: "custom:chore-board-card", title: "Chores" };
  }

  @property({ attribute: false }) public hass!: HomeAssistant;
  @property({ attribute: false }) public config!: ChoreBoardCardConfig;
  @property({ attribute: false }) public lovelace?: any;

  @state() private _items: TodoItem[] = [];
  @state() private _currentUser: string = "";
  @state() private _knownMembers: string[] = [];
  @state() private _showAttributionPopup = false;
  @state() private _pendingTask: TodoItem | null = null;

  public async setConfig(config: ChoreBoardCardConfig) {
    if (!config.entity) {
      throw new Error("Chore Board: entity is required");
    }
    this.config = config;
  }

  public async connectedCallback() {
    super.connectedCallback();
    await this._loadState();
    // Refresh periodically
    this._refreshInterval = setInterval(() => this._loadState(),
      (this.config.refresh_interval || 30) * 1000);
  }

  public disconnectedCallback() {
    super.disconnectedCallback();
    if (this._refreshInterval) {
      clearInterval(this._refreshInterval);
    }
  }

  private _refreshInterval: number | null = null;

  private async _loadState() {
    if (!this.hass) return;

    // Get current user from HA
    const user = this.hass.user;
    this._currentUser = user?.name || "Unknown";

    // Get known members from config
    const configEntry = this.hass.config.components.find((c: string) => c === "chore_board");
    if (configEntry) {
      // Members are in the config entry data
      const entries = this.hass.config.entries;
      for (const entry of entries) {
        if (entry.domain === "chore_board") {
          this._knownMembers = (entry.data.members || []).map((m: any) => m.name);
          break;
        }
      }
    }

    // Get todo items
    try {
      const result = await this.hass.callService("todo", "get_items", {
        entity_id: this.config.entity,
      }, { returnResponse: true });
      const items = result[this.config.entity]?.items || [];
      this._items = items;
    } catch (e) {
      console.error("Failed to load todo items:", e);
    }
  }

  private async _handleComplete(item: TodoItem) {
    // Check if current user is a known member
    const isKnownMember = this._knownMembers.includes(this._currentUser);

    if (!isKnownMember) {
      // Show attribution popup
      this._pendingTask = item;
      this._showAttributionPopup = true;
      this.requestUpdate();
      return;
    }

    // User is known — award points directly
    await this._awardPoints(item, this._currentUser);
  }

  private async _handleAttribution(memberName: string) {
    if (!this._pendingTask) return;

    await this._awardPoints(this._pendingTask, memberName);
    this._showAttributionPopup = false;
    this._pendingTask = null;
    this.requestUpdate();
  }

  private async _awardPoints(item: TodoItem, memberName: string) {
    try {
      // Call the award_points service
      await this.hass.callService("chore_board", "award_points", {
        task_id: `${this.config.entity}-${item.uid}`,
        member_id: memberName.toLowerCase().replace(/\s+/g, "_"),
      });

      // Remove the completed item from our local list
      this._items = this._items.filter(i => i.uid !== item.uid);
    } catch (e) {
      console.error("Failed to award points:", e);
    }
  }

  protected render(): TemplateResult {
    return html`
      <div class="card-container">
        <div class="card-header">
          <span class="title">${this.config.title || "Chores"}</span>
          <span class="user">${this._currentUser}</span>
        </div>
        <div class="items">
          ${this._items.map(item => this._renderItem(item))}
          ${this._items.length === 0 ? html`<div class="empty">All done! 🎉</div>` : nothing}
        </div>
        ${this._showAttributionPopup ? this._renderAttributionPopup() : nothing}
      </div>
    `;
  }

  private _renderItem(item: TodoItem) {
    const isCompleted = item.status === "completed";
    return html`
      <div class="item ${isCompleted ? "completed" : ""}">
        <div class="item-content">
          <span class="item-title">${item.summary}</span>
          ${item.description ? html`<span class="item-desc">${item.description}</span>` : nothing}
        </div>
        ${!isCompleted ? html`
          <button class="complete-btn" @click=${() => this._handleComplete(item)}>✓</button>
        ` : nothing}
      </div>
    `;
  }

  private _renderAttributionPopup() {
    return html`
      <div class="popup-overlay">
        <div class="popup">
          <h3>Who completed this?</h3>
          <p>"${this._pendingTask?.summary}"</p>
          <div class="member-buttons">
            ${this._knownMembers.map(member => html`
              <button class="member-btn" @click=${() => this._handleAttribution(member)}>
                ${member}
              </button>
            `)}
          </div>
          <button class="cancel-btn" @click=${() => {
            this._showAttributionPopup = false;
            this._pendingTask = null;
            this.requestUpdate();
          }}>Cancel</button>
        </div>
      </div>
    `;
  }

  static styles = css`
    :host {
      display: block;
    }
    .card-container {
      padding: 16px;
    }
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }
    .title {
      font-size: 18px;
      font-weight: bold;
    }
    .user {
      font-size: 14px;
      color: var(--primary-text-color);
      opacity: 0.7;
    }
    .items {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .item {
      display: flex;
      align-items: center;
      padding: 12px;
      background: var(--secondary-background-color);
      border-radius: 8px;
    }
    .item.completed {
      opacity: 0.5;
    }
    .item-content {
      flex: 1;
    }
    .item-title {
      display: block;
      font-weight: 500;
    }
    .item-desc {
      display: block;
      font-size: 12px;
      opacity: 0.7;
    }
    .complete-btn {
      background: var(--primary-color);
      color: white;
      border: none;
      border-radius: 50%;
      width: 32px;
      height: 32px;
      cursor: pointer;
      font-size: 16px;
    }
    .complete-btn:hover {
      opacity: 0.8;
    }
    .empty {
      text-align: center;
      padding: 24px;
      opacity: 0.5;
    }
    .popup-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
    }
    .popup {
      background: var(--card-background-color);
      border-radius: 12px;
      padding: 24px;
      max-width: 400px;
      width: 90%;
    }
    .popup h3 {
      margin: 0 0 8px;
    }
    .popup p {
      margin: 0 0 16px;
      opacity: 0.7;
    }
    .member-buttons {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 16px;
    }
    .member-btn {
      flex: 1;
      min-width: 80px;
      padding: 12px;
      background: var(--primary-color);
      color: white;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      font-size: 14px;
    }
    .member-btn:hover {
      opacity: 0.8;
    }
    .cancel-btn {
      width: 100%;
      padding: 12px;
      background: transparent;
      border: 1px solid var(--primary-color);
      border-radius: 8px;
      cursor: pointer;
      color: var(--primary-color);
    }
  `;
}

// Register the card
if (customElements.get("chore-board-card")) {
  console.warn("Chore Board card already registered");
} else {
  customElements.define("chore-board-card", ChoreBoardCard);
}
