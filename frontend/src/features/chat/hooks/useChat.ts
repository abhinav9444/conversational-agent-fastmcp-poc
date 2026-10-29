"use client";

import { useCallback, useState } from "react";
import { sendChatMessage } from "../services/chatService";
import type { ChatMessage } from "../types/chat";

function makeId(): string {
  return typeof crypto !== "undefined" && "randomUUID" in crypto
    ? crypto.randomUUID()
    : `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function timestamp(): string {
  return new Date().toISOString();
}

const welcomeMessage: ChatMessage = {
  id: "orion-welcome",
  role: "assistant",
  content:
    "Hi! I’m Orion, your prospect data assistant. Ask me about opportunity value, industries, stages, regions, or risk levels. I’ll retrieve relevant records through the connected data tool.",
  // Keep the server-rendered welcome message identical during browser hydration.
  createdAt: "2000-01-01T00:00:00.000Z"
};

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([welcomeMessage]);
  const [conversationId, setConversationId] = useState<string>();
  const [isSending, setIsSending] = useState(false);

  const sendMessage = useCallback(
    async (rawMessage: string) => {
      const message = rawMessage.trim();
      if (!message || isSending) return;

      const userMessage: ChatMessage = {
        id: makeId(),
        role: "user",
        content: message,
        createdAt: timestamp()
      };
      const pendingId = makeId();

      setMessages((current) => [
        ...current,
        userMessage,
        {
          id: pendingId,
          role: "assistant",
          content: "Looking up the prospect data…",
          createdAt: timestamp(),
          status: "sending"
        }
      ]);
      setIsSending(true);

      try {
        const response = await sendChatMessage(message, conversationId);
        setConversationId(response.conversation_id);
        setMessages((current) =>
          current.map((item) =>
            item.id === pendingId
              ? {
                  ...item,
                  content: response.answer,
                  toolsInvoked: response.tools_invoked,
                  status: undefined
                }
              : item
          )
        );
      } catch (error) {
        const detail =
          error instanceof Error
            ? error.message
            : "Something went wrong while contacting Orion.";
        setMessages((current) =>
          current.map((item) =>
            item.id === pendingId
              ? {
                  ...item,
                  content: detail,
                  status: "error"
                }
              : item
          )
        );
      } finally {
        setIsSending(false);
      }
    },
    [conversationId, isSending]
  );

  const startNewChat = useCallback(() => {
    setConversationId(undefined);
    setMessages([
      {
        ...welcomeMessage,
        id: makeId(),
        createdAt: timestamp()
      }
    ]);
  }, []);

  return { messages, isSending, conversationId, sendMessage, startNewChat };
}