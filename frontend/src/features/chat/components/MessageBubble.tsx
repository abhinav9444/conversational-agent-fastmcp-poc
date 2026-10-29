import type { ChatMessage } from "../types/chat";

interface MessageBubbleProps {
  message: ChatMessage;
}

function formatTime(value: string): string {
  return new Intl.DateTimeFormat(undefined, {
    hour: "numeric",
    minute: "2-digit"
  }).format(new Date(value));
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <article className={`message-row ${isUser ? "message-row-user" : "message-row-assistant"}`}>
      {!isUser && <div className="avatar avatar-orion" aria-hidden="true">O</div>}
      <div className="message-stack">
        <div className="message-meta">
          <span>{isUser ? "You" : "Orion"}</span>
          <time dateTime={message.createdAt}>{formatTime(message.createdAt)}</time>
        </div>
        <div
          className={[
            "message-bubble",
            isUser ? "message-bubble-user" : "message-bubble-assistant",
            message.status === "error" ? "message-bubble-error" : ""
          ].filter(Boolean).join(" ")}
        >
          {message.status === "sending" && <span className="typing-indicator" aria-hidden="true"><i /><i /><i /></span>}
          <p>{message.content}</p>
        </div>
        {!isUser && message.toolsInvoked && message.toolsInvoked.length > 0 && (
          <div className="tool-trace" title="Tools used for this answer">
            <span className="tool-trace-dot" />
            Data tool used: {message.toolsInvoked.join(", ")}
          </div>
        )}
        {!isUser && message.status === "error" && (
          <div className="error-hint">Check that the API, MCP server, and local model are running.</div>
        )}
      </div>
      {isUser && <div className="avatar avatar-user" aria-hidden="true">Y</div>}
    </article>
  );
}