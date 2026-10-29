export type ChatRole = "assistant" | "user";

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  createdAt: string;
  toolsInvoked?: string[];
  status?: "sending" | "error";
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  conversation_id: string;
  answer: string;
  tools_invoked: string[];
}

export interface ChatApiError {
  detail?: string;
}