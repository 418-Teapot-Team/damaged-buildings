import { AgentConfig } from "../api/ai";

class ActiveChats {
  private chats: Map<number, AgentConfig>;

  constructor() {
    this.chats = new Map();
  }

  startChat(userID: number, config: AgentConfig) {
    this.chats.set(userID, config);
  }

  endChat(userID: number) {
    this.chats.delete(userID);
  }

  isChatActive(userID: number): boolean {
    return this.chats.has(userID);
  }

  getChatAgent(userID: number): AgentConfig | undefined {
    return this.chats.get(userID);
  }
}

export default new ActiveChats();
