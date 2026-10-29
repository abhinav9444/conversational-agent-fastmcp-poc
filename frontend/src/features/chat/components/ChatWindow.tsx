"use client";

import { useEffect, useRef } from "react";
import { ChatComposer } from "./ChatComposer";
import { MessageBubble } from "./MessageBubble";
import { useChat } from "../hooks/useChat";

const suggestions = [
  "Show high-risk prospects in Europe",
  "Which opportunities have the highest value?",
  "Summarize pipeline value by stage",
  "Which industries are represented?"
];

export function ChatWindow() {
  const { messages, isSending, conversationId, sendMessage, startNewChat } = useChat();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages]);

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand-lockup">
          <div>
            <div className="brand-name">orion</div>
            <div className="brand-subtitle">DATA INTELLIGENCE</div>
          </div>
        </div>

        <button className="new-chat-button" type="button" onClick={startNewChat}>
          <span aria-hidden="true">＋</span> New conversation
        </button>

        <div className="sidebar-section-label">WORKSPACE</div>
        <div className="workspace-item workspace-item-active">
          <span className="workspace-icon" aria-hidden="true">◈</span>
          <span>Prospect intelligence</span>
          <span className="active-indicator" />
        </div>

        <div className="sidebar-spacer" />
        <div className="connection-card">
          <div className="connection-heading"><span className="status-dot" /> Local environment</div>
          <p>Private demo workspace</p>
          <div className="connection-divider" />
          <div className="connection-detail"><span>LLM</span><strong>Ollama</strong></div>
          <div className="connection-detail"><span>Data access</span><strong>Read-only MCP</strong></div>
        </div>
        <div className="sidebar-footer"><span className="footer-orbit">◉</span> ORION POC <span className="footer-version">v0.1</span></div>
      </aside>

      <section className="chat-panel">
        <header className="topbar">
          <div className="topbar-title">
            <div>
              <h1>Prospect intelligence</h1>
              <div className="topbar-subtitle"><span className="status-dot" /> Connected to local agent</div>
            </div>
          </div>
          <div className="topbar-right">
            <span className="privacy-pill"><span aria-hidden="true">◇</span> Local &amp; private</span>
            <button className="icon-button" type="button" onClick={startNewChat} title="Start a new conversation" aria-label="Start a new conversation">↻</button>
          </div>
        </header>

        <div className="messages-scroll">
          <div className="conversation-column">
            <div className="date-divider"><span>YOUR DATA WORKSPACE</span></div>
            <div className="messages-list" aria-live="polite">
              {messages.map((message) => <MessageBubble key={message.id} message={message} />)}
            </div>
            {messages.length === 1 && (
              <section className="suggestions-section" aria-label="Suggested questions">
                <div className="suggestions-heading">Try asking</div>
                <div className="suggestion-grid">
                  {suggestions.map((suggestion, index) => (
                    <button
                      key={suggestion}
                      className="suggestion-card"
                      type="button"
                      onClick={() => void sendMessage(suggestion)}
                      disabled={isSending}
                    >
                      <span className={`suggestion-icon suggestion-icon-${index + 1}`} aria-hidden="true">{["↗", "◈", "▤", "⌘"][index]}</span>
                      <span>{suggestion}</span>
                      <span className="suggestion-arrow" aria-hidden="true">↗</span>
                    </button>
                  ))}
                </div>
              </section>
            )}
            <div ref={bottomRef} />
          </div>
        </div>

        <footer className="composer-area">
          <div className="composer-inner">
            <ChatComposer disabled={isSending} onSend={(message) => void sendMessage(message)} />
            <p className="disclaimer">Orion answers using retrieved prospect data. Demo records are synthetic and for testing only.</p>
          </div>
        </footer>
        {conversationId && <span className="conversation-id" title={conversationId}>Conversation active</span>}
      </section>
    </main>
  );
}