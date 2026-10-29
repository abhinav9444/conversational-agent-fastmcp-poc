import { postJson } from "@/lib/apiClient";
import type { ChatRequest, ChatResponse } from "../types/chat";

export function sendChatMessage(
  message: string,
  conversationId?: string
): Promise<ChatResponse> {
  const payload: ChatRequest = {
    message,
    ...(conversationId ? { conversation_id: conversationId } : {})
  };

  return postJson<ChatResponse, ChatRequest>("/chat", payload);
}