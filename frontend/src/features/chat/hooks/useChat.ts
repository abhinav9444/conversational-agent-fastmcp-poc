"use client";

import { useCallback, useEffect, useState } from "react";
import { sendChatMessage } from "../services/chatService";
import type { ChatMessage } from "../types/chat";

const STORAGE_KEY = "orion.chat-sessions.v1";

export interface ChatSession {
  id: string;
  title: string;
  conversationId?: string;
  messages: ChatMessage[];
  updatedAt: string;
}

function makeId(): string {
  return typeof crypto !== "undefined" && "randomUUID" in crypto
    ? crypto.randomUUID()
    : `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function timestamp(): string {
  return new Date().toISOString();
}

function makeWelcomeMessage(): ChatMessage {
  return {
    id: "orion-welcome",
    role: "assistant",
    content: "Ask a question about your prospect pipeline.",
    createdAt: "2000-01-01T00:00:00.000Z"
  };
}

function makeSession(): ChatSession {
  return {
    id: makeId(),
    title: "New conversation",
    messages: [makeWelcomeMessage()],
    updatedAt: timestamp()
  };
}

function isChatMessage(value: unknown): value is ChatMessage {
  if (!value || typeof value !== "object") return false;
  const message = value as Partial<ChatMessage>;
  return typeof message.id === "string"
    && (message.role === "assistant" || message.role === "user")
    && typeof message.content === "string"
    && typeof message.createdAt === "string";
}

function loadSessions(): ChatSession[] {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.filter((item): item is ChatSession => {
      if (!item || typeof item !== "object") return false;
      const session = item as Partial<ChatSession>;
      return typeof session.id === "string"
        && typeof session.title === "string"
        && typeof session.updatedAt === "string"
        && Array.isArray(session.messages)
        && session.messages.every(isChatMessage);
    }).map((session) => ({
      ...session,
      messages: session.messages.filter((message) => message.status !== "sending")
    }));
  } catch {
    return [];
  }
}

export function useChat() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [isHydrated, setIsHydrated] = useState(false);
  const [isSending, setIsSending] = useState(false);

  useEffect(() => {
    const saved = loadSessions();
    const initialSessions = saved.length ? saved : [makeSession()];
    setSessions(initialSessions);
    setActiveSessionId(initialSessions[0].id);
    setIsHydrated(true);
  }, []);

  useEffect(() => {
    if (!isHydrated) return;
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
    } catch {
      // Chat remains usable for this tab even if browser storage is unavailable.
    }
  }, [sessions, isHydrated]);

  const activeSession = sessions.find((session) => session.id === activeSessionId) ?? null;

  const updateSession = useCallback((sessionId: string, updater: (session: ChatSession) => ChatSession) => {
    setSessions((current) => current.map((session) =>
      session.id === sessionId ? updater(session) : session
    ));
  }, []);

  const sendMessage = useCallback(async (rawMessage: string) => {
    const message = rawMessage.trim();
    if (!message || isSending || !activeSession) return;

    const sessionId = activeSession.id;
    const userMessage: ChatMessage = {
      id: makeId(),
      role: "user",
      content: message,
      createdAt: timestamp()
    };
    const pendingId = makeId();
    const now = timestamp();

    updateSession(sessionId, (session) => ({
      ...session,
      title: session.title === "New conversation" ? message.slice(0, 42) : session.title,
      updatedAt: now,
      messages: [
        ...session.messages,
        userMessage,
        {
          id: pendingId,
          role: "assistant",
          content: "Thinking…",
          createdAt: now,
          status: "sending"
        }
      ]
    }));
    setIsSending(true);

    try {
      const response = await sendChatMessage(message, activeSession.conversationId);
      updateSession(sessionId, (session) => ({
        ...session,
        conversationId: response.conversation_id,
        updatedAt: timestamp(),
        messages: session.messages.map((item) => item.id === pendingId
          ? { ...item, content: response.answer, toolsInvoked: response.tools_invoked, status: undefined }
          : item)
      }));
    } catch (error) {
      const detail = error instanceof Error
        ? error.message
        : "Something went wrong while contacting Orion.";
      updateSession(sessionId, (session) => ({
        ...session,
        updatedAt: timestamp(),
        messages: session.messages.map((item) => item.id === pendingId
          ? { ...item, content: detail, status: "error" }
          : item)
      }));
    } finally {
      setIsSending(false);
    }
  }, [activeSession, isSending, updateSession]);

  const startNewChat = useCallback(() => {
    const session = makeSession();
    setSessions((current) => [session, ...current]);
    setActiveSessionId(session.id);
  }, []);

  const selectSession = useCallback((sessionId: string) => {
    if (isSending) return;
    setActiveSessionId(sessionId);
  }, [isSending]);

  const deleteSession = useCallback((sessionId: string) => {
    if (isSending) return;
    setSessions((current) => {
      const remaining = current.filter((session) => session.id !== sessionId);
      if (remaining.length === 0) {
        const fresh = makeSession();
        setActiveSessionId(fresh.id);
        return [fresh];
      }
      if (activeSessionId === sessionId) setActiveSessionId(remaining[0].id);
      return remaining;
    });
  }, [activeSessionId, isSending]);

  return {
    sessions,
    activeSession,
    activeSessionId,
    isHydrated,
    isSending,
    messages: activeSession?.messages ?? [],
    conversationId: activeSession?.conversationId,
    sendMessage,
    startNewChat,
    selectSession,
    deleteSession
  };
}
