/**
 * Chore Board Admin Panel
 *
 * HA custom panel for managing chores, members, and LLM config.
 * Requires HA admin permissions.
 */

import {
  css,
  html,
  LitElement,
  nothing,
  TemplateResult,
} from "lit";
import { customElement, property, state } from "lit/decorators.js";
import { HomeAssistant } from "custom-card-helpers";

// Types
export interface ChoreItem {
  id: string;
  title: string;
  points: number;
  assigned_to?: string;
  active: boolean;
}

export interface MemberItem {
  id: string;
  name: string;
  ha_user_id?: string;
  todoist_username?: string;
  avatar?: string;
}

export interface LLMConfig {
  llm_base_url: string;
  llm_api_key: string;
  llm_model: string;
}

export interface BoardState {
  chores: ChoreItem[];
  members: MemberItem[];
  scores: Record<string, number>;
  history: any[];
}

@customElement("chore-board-admin")
export class ChoreBoardAdmin extends LitElement {
  @property({ attribute: false }) public hass!: HomeAssistant;
  @property({ type: Boolean }) public isAdmin = false;
  @state() private _activeTab = "chores";
  @state() private _boardState: BoardState | null = null;
  @state() private _llmConfig: LLMConfig = {
    llm_base_url: "",
    llm_api_key: "",
    llm_model: "gpt-4o-mini",
  };
  @state() private _saving = false;

  protected async connectedCallback() {
    super.connectedCallback();
    // Check admin status
    this.isAdmin = this.hass.user?.admin === true;
    if (!this.isAdmin) {
      return;
    }
    await this._loadState();
  }

  private async _loadState() {
    try {
      const state = await this.hass.callWS({
        type: "chore_board/get_state",
      });
      this._boardState = state;
      this._llmConfig = state.llm_config || this._llmConfig;
    } catch (e) {
      console.error("Failed to load Chore Board state:", e);
    }
  }

  private async _saveChore(chore: ChoreItem) {
    this._saving = true;
    try {
      await this.hass.callService("chore_board", "adjust_chore_points", {
        chore_id: chore.id,
        points: chore.points,
      });
      await this._loadState();
    } catch (e) {
      console.error("Failed to save chore:", e);
    } finally {
      this._saving = false;
    }
  }

  private async _saveMember(memberId: string, updates: Partial<MemberItem>) {
    this._saving = true;
    try {
      await this.hass.callService("chore_board", "update_member", {
        member_id: memberId,
        ...updates,
      });
      await this._loadState();
    } catch (e) {
      console.error("Failed to save member:", e);
    } finally {
      this._saving = false;
    }
  }

  private async _saveLLMConfig(config: LLMConfig) {
    this._saving = true;
    try {
      await this.hass.callService("chore_board", "update_llm_config", {
        base_url: config.llm_base_url,
        api_key: config.llm_api_key,
        model: config.llm_model,
      });
      this._llmConfig = config;
    } catch (e) {
      console.error("Failed to save LLM config:", e);
    } finally {
      this._saving = false;
    }
  }

  protected render() {
    if (!this.isAdmin) {
      return html`
        <ha-card header="Chore Board Admin">
          <div class="no-access">
            <ha-icon icon="mdi:lock"></ha-icon>
            <p>Admin access required</p>
          </div>
        </ha-card>
      `;
    }

    return html`
      <ha-card header="Chore Board Admin">
        <div class="tabs">
          <button class="${this._activeTab === 'chores' ? 'active' : ''}"
                  @click=${() => this._activeTab = 'chores'}>Chores</button>
          <button class="${this._activeTab === 'members' ? 'active' : ''}"
                  @click=${() => this._activeTab = 'members'}>Members</button>
          <button class="${this._activeTab === 'llm' ? 'active' : ''}"
                  @click=${() => this._activeTab = 'llm'}>LLM Config</button>
        </div>
        <div class="content">
          ${this._activeTab === 'chores' ? this._renderChores() : nothing}
          ${this._activeTab === 'members' ? this._renderMembers() : nothing}
          ${this._activeTab === 'llm' ? this._renderLLMConfig() : nothing}
        </div>
      </ha-card>
    `;
  }

  private _renderChores() {
    if (!this._boardState) return html`<p>Loading...</p>`;

    return html`
      <div class="chores-list">
        ${this._boardState.chores.map(chore => html`
          <div class="chore-item">
            <div class="chore-info">
              <span class="chore-title">${chore.title}</span>
              <span class="chore-id">${chore.id}</span>
            </div>
            <div class="chore-points">
              <label>Points:</label>
              <input type="number"
                     .value=${chore.points}
                     @change=${(e: Event) => {
                       const updated = { ...chore, points: parseInt((e.target as HTMLInputElement).value) };
                       this._saveChore(updated);
                     }}
                     min="1"
                     max="100"
                     class="points-input"
              />
            </div>
          </div>
        `)}
      </div>
    `;
  }

  private _renderMembers() {
    if (!this._boardState) return html`<p>Loading...</p>`;

    // Get all HA users for dropdown
    const haUsers = this.hass.users || [];

    return html`
      <div class="members-list">
        ${this._boardState.members.map(member => html`
          <div class="member-item">
            <div class="member-info">
              <span class="member-name">${member.name}</span>
              <span class="member-id">${member.id}</span>
            </div>
            <div class="member-links">
              <div class="link-field">
                <label>HA User:</label>
                <select @change=${(e: Event) => {
                  const userId = (e.target as HTMLSelectElement).value || undefined;
                  this._saveMember(member.id, { ha_user_id: userId });
                }}>
                  <option value="">None</option>
                  ${haUsers.map(user => html`
                    <option value=${user.id} ?selected=${user.id === member.ha_user_id}>
                      ${user.name}
                    </option>
                  `)}
                </select>
              </div>
              <div class="link-field">
                <label>Todoist:</label>
                <input type="text"
                       .value=${member.todoist_username || ""}
                       @change=${(e: Event) => {
                         const username = (e.target as HTMLInputElement).value || undefined;
                         this._saveMember(member.id, { todoist_username: username });
                       }}
                       placeholder="Todoist username"
                />
              </div>
            </div>
          </div>
        `)}
      </div>
    `;
  }

  private _renderLLMConfig() {
    return html`
      <div class="llm-config">
        <div class="config-field">
          <label>Base URL:</label>
          <input type="text"
                 .value=${this._llmConfig.llm_base_url}
                 @change=${(e: Event) => {
                   const config = { ...this._llmConfig, llm_base_url: (e.target as HTMLInputElement).value };
                   this._saveLLMConfig(config);
                 }}
                 placeholder="https://api.openai.com/v1"
          />
          <small>OpenAI-compatible API base URL (leave empty for default)</small>
        </div>
        <div class="config-field">
          <label>API Key:</label>
          <input type="password"
                 .value=${this._llmConfig.llm_api_key}
                 @change=${(e: Event) => {
                   const config = { ...this._llmConfig, llm_api_key: (e.target as HTMLInputElement).value };
                   this._saveLLMConfig(config);
                 }}
                 placeholder="sk-..."
          />
        </div>
        <div class="config-field">
          <label>Model:</label>
          <input type="text"
                 .value=${this._llmConfig.llm_model}
                 @change=${(e: Event) => {
                   const config = { ...this._llmConfig, llm_model: (e.target as HTMLInputElement).value };
                   this._saveLLMConfig(config);
                 }}
                 placeholder="gpt-4o-mini"
          />
        </div>
        <div class="fallback-note">
          <ha-alert alert-type="info">
            If the LLM call fails, scoring falls back to ${this._boardState?.chores.length ? 'default 10 points' : '10 points'}.
          </ha-alert>
        </div>
      </div>
    `;
  }

  static styles = css`
    :host {
      display: block;
    }
    ha-card {
      margin: 16px;
    }
    .tabs {
      display: flex;
      border-bottom: 1px solid var(--divider-color);
      margin-bottom: 16px;
    }
    .tabs button {
      padding: 12px 24px;
      background: none;
      border: none;
      cursor: pointer;
      font-size: 14px;
      color: var(--primary-text-color);
      opacity: 0.7;
    }
    .tabs button.active {
      opacity: 1;
      border-bottom: 2px solid var(--primary-color);
      font-weight: bold;
    }
    .content {
      padding: 0 16px 16px;
    }
    .no-access {
      text-align: center;
      padding: 48px;
      color: var(--primary-text-color);
      opacity: 0.7;
    }
    .no-access ha-icon {
      font-size: 48px;
      margin-bottom: 16px;
    }
    .chores-list, .members-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .chore-item, .member-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px;
      background: var(--secondary-background-color);
      border-radius: 8px;
    }
    .chore-info, .member-info {
      display: flex;
      flex-direction: column;
    }
    .chore-title, .member-name {
      font-weight: 500;
    }
    .chore-id, .member-id {
      font-size: 12px;
      opacity: 0.6;
    }
    .chore-points {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .points-input {
      width: 60px;
      padding: 4px 8px;
      border: 1px solid var(--primary-color);
      border-radius: 4px;
      text-align: center;
    }
    .member-links {
      display: flex;
      gap: 16px;
      align-items: center;
    }
    .link-field {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .link-field label {
      font-size: 12px;
      opacity: 0.7;
    }
    .link-field input, .link-field select {
      padding: 4px 8px;
      border: 1px solid var(--primary-color);
      border-radius: 4px;
      min-width: 150px;
    }
    .llm-config {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .config-field {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .config-field label {
      font-weight: 500;
    }
    .config-field input {
      padding: 8px;
      border: 1px solid var(--primary-color);
      border-radius: 4px;
    }
    .config-field small {
      opacity: 0.6;
      font-size: 12px;
    }
    .fallback-note {
      margin-top: 16px;
    }
  `;
}

if (customElements.get("chore-board-admin")) {
  console.warn("Chore Board admin already registered");
} else {
  customElements.define("chore-board-admin", ChoreBoardAdmin);
}
