"use client";

import { FormEvent, KeyboardEvent, useState } from "react";

interface ChatComposerProps {
  disabled?: boolean;
  onSend: (message: string) => void;
}

export function ChatComposer({ disabled = false, onSend }: ChatComposerProps) {
  const [value, setValue] = useState("");

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const message = value.trim();
    if (!message || disabled) return;
    onSend(message);
    setValue("");
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      event.currentTarget.form?.requestSubmit();
    }
  }

  return (
    <form className="composer" onSubmit={submit}>
      <label className="sr-only" htmlFor="chat-message">Message Orion</label>
      <textarea
        id="chat-message"
        value={value}
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask about your prospect pipeline…"
        rows={1}
        maxLength={4000}
        disabled={disabled}
      />
      <div className="composer-footer">
        <span className="composer-hint">Enter to send · Shift + Enter for a new line</span>
        <button className="send-button" type="submit" disabled={disabled || !value.trim()} aria-label="Send message">
          {disabled ? <span className="send-spinner" /> : <span aria-hidden="true">↑</span>}
        </button>
      </div>
    </form>
  );
}