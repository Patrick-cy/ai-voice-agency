export interface Message {
  role: "user" | "assistant" | "system";
  content: string;
}

export class SessionMemory {
  private history: Message[] = [];
  private customerName: string | undefined;

  addMessage(role: "user" | "assistant", content: string) {
    this.history.push({ role, content });
  }

  getHistory(): Message[] {
    return this.history;
  }

  setName(name: string) {
    this.customerName = name;
  }

  getName(): string | undefined {
    return this.customerName;
  }

  clear() {
    this.history = [];
    this.customerName = undefined;
  }
}