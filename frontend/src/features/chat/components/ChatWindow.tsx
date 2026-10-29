"use client";

import { useEffect, useRef } from "react";
import { ChatComposer } from "./ChatComposer";
import { MessageBubble } from "./MessageBubble";
import { useChat } from "../hooks/useChat";

export function ChatWindow() {
  const {
    sessions,
    activeSession,
    activeSessionId,
    isHydrated,
    isSending,
    messages,
    sendMessage,
    startNewChat,
    selectSession,
    deleteSession
  } = useChat();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages]);

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand-lockup">
          <div className="brand-name">orion</div>
        </div>
        <button className="new-chat-button" type="button" onClick={startNewChat}>
          <span aria-hidden="true">＋</span> New chat
        </button>
        <div className="history-heading">RECENT CHATS</div>
        <nav className="history-list" aria-label="Chat history">
          {!isHydrated && <p className="history-empty">Loading chats…</p>}
          {isHydrated && sessions.length === 0 && <p className="history-empty">No chats yet</p>}
          {sessions.map((session) => (
            <div className={`history-item ${session.id === activeSessionId ? "history-item-active" : ""}`} key={session.id}>
              <button
                className="history-select"
                type="button"
                onClick={() => selectSession(session.id)}
                disabled={isSending}
                title={session.title}
              >
                <span className="history-chat-icon" aria-hidden="true">↳</span>
                <span>{session.title}</span>
              </button>
              <button
                className="history-delete"
                type="button"
                onClick={() => deleteSession(session.id)}
                disabled={isSending}
                aria-label={`Delete chat: ${session.title}`}
                title="Delete chat"
              >×</button>
            </div>
          ))}
        </nav>
        <div className="sidebar-footer">ORION · LOCAL CHAT</div>
      </aside>

      <section className="chat-panel">
        <header className="topbar">
          <div>
            <h1>{activeSession?.title || "New chat"}</h1>
            <div className="topbar-subtitle">Prospect intelligence</div>
          </div>
        </header>

        <div className="messages-scroll">
          <div className="conversation-column">
            {messages.length <= 1 && (
              <div className="empty-state">
                <h2>What would you like to know?</h2>
                <p>Ask a question about your prospect pipeline.</p>
                <div className="quick-prompts">
                  <button type="button" onClick={() => void sendMessage("Show high-risk prospects in Europe")} disabled={isSending}>High-risk prospects in Europe <span>↗</span></button>
                  <button type="button" onClick={() => void sendMessage("Summarize pipeline value by stage")} disabled={isSending}>Pipeline value by stage <span>↗</span></button>
                </div>
              </div>
            )}
            <div className="messages-list" aria-live="polite">
              {messages.filter((message) => message.id !== "orion-welcome").map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}
            </div>
            <div ref={bottomRef} />
          </div>
        </div>

        <footer className="composer-area">
          <div className="composer-inner">
            <ChatComposer disabled={isSending || !isHydrated} onSend={(message) => void sendMessage(message)} />
            <p className="disclaimer">Answers are based on retrieved prospect data.</p>
          </div>
        </footer>
      </section>
    </main>
  );
}
