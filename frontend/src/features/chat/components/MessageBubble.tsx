import type { ReactNode } from "react";
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

function renderInline(text: string): ReactNode[] {
  return text.split(/(\*\*[^*]+\*\*)/g).map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={index}>{part.slice(2, -2)}</strong>;
    }
    return part;
  });
}

function renderMessageContent(content: string): ReactNode {
  const lines = content.split(/\r?\n/);
  const blocks: Array<{ type: "paragraph" | "list"; lines: string[] }> = [];

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line) continue;
    const isListItem = /^[-*]\s+/.test(line);
    const type = isListItem ? "list" : "paragraph";
    const previous = blocks[blocks.length - 1];

    if (previous && previous.type === type) {
      previous.lines.push(isListItem ? line.replace(/^[-*]\s+/, "") : line);
    } else {
      blocks.push({
        type,
        lines: [isListItem ? line.replace(/^[-*]\s+/, "") : line]
      });
    }
  }

  return blocks.map((block, blockIndex) => {
    if (block.type === "list") {
      return (
        <ul className="answer-list" key={blockIndex}>
          {block.lines.map((line, lineIndex) => (
            <li key={lineIndex}>{renderInline(line)}</li>
          ))}
        </ul>
      );
    }

    return (
      <p className="answer-paragraph" key={blockIndex}>
        {block.lines.map((line, lineIndex) => (
          <span key={lineIndex}>
            {lineIndex > 0 && " "}
            {renderInline(line)}
          </span>
        ))}
      </p>
    );
  });
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <article className={`message-row ${isUser ? "message-row-user" : "message-row-assistant"}`}>
      {!isUser && <div className="avatar avatar-orion" aria-hidden="true">O</div>}
      <div className="message-stack">
        <div className="message-meta">
          <span>{isUser ? "You" : "Orion"}</span>
          {message.id !== "orion-welcome" && (
            <time dateTime={message.createdAt}>{formatTime(message.createdAt)}</time>
          )}
        </div>
        <div
          className={[
            "message-bubble",
            isUser ? "message-bubble-user" : "message-bubble-assistant",
            message.status === "error" ? "message-bubble-error" : ""
          ].filter(Boolean).join(" ")}
        >
          {message.status === "sending" && <span className="typing-indicator" aria-hidden="true"><i /><i /><i /></span>}
          <div className="message-content">{renderMessageContent(message.content)}</div>
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