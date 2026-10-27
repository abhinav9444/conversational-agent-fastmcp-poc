"use client";

import { FormEvent, KeyboardEvent, useEffect, useRef, useState } from "react";

type Message = { role: "user" | "assistant"; content: string; tools?: string[] };
type Prospect = { name: string; detail: string; score: number; region: string; stage: string; risk: string };

const prospects: Prospect[] = [
  { name: "Northwind Bio", detail: "Entered phase III, 12 Sep", score: 98, region: "Europe", stage: "Clinical", risk: "Low" },
  { name: "Wren Biosciences", detail: "Raised a $35M series A", score: 88, region: "North America", stage: "Discovery", risk: "Medium" },
  { name: "Morrow Therapeutics", detail: "First patient dosed in phase I", score: 84, region: "Europe", stage: "Clinical", risk: "High" },
  { name: "Kestrel Labs", detail: "New VP of CMC joined", score: 80, region: "Asia Pacific", stage: "Discovery", risk: "Low" },
  { name: "Tamsin Pharma", detail: "Phase II enrolment complete", score: 66, region: "Europe", stage: "Negotiation", risk: "Medium" },
];

const suggestions = ["Why is Wren the strongest?", "What changed since Friday?", "Who should I call first?"];

export default function Home() {
  const [tab, setTab] = useState("Today");
  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: "Good morning. Two things are due, and Wren Biosciences is the strongest new one: it raised money for manufacturing and has no partner yet." }
  ]);
  const [busy, setBusy] = useState(false);
  const [apiStatus, setApiStatus] = useState<"checking" | "ready" | "offline">("checking");
  const [conversationId, setConversationId] = useState<string | undefined>();
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch((process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080") + "/health")
      .then((r) => { if (!r.ok) throw new Error(); setApiStatus("ready"); })
      .catch(() => setApiStatus("offline"));
  }, []);
  useEffect(() => endRef.current?.scrollIntoView({ behavior: "smooth" }), [messages, busy]);

  async function sendMessage(text = draft) {
    const message = text.trim();
    if (!message || busy) return;
    setMessages((prev) => [...prev, { role: "user", content: message }]);
    setDraft("");
    setBusy(true);
    try {
      const response = await fetch((process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080") + "/chat", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, ...(conversationId ? { conversation_id: conversationId } : {}) }),
      });
      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(body.detail || `API returned ${response.status}`);
      }
      const result = await response.json();
      setConversationId(result.conversation_id);
      setMessages((prev) => [...prev, { role: "assistant", content: result.answer, tools: result.tools_invoked || [] }]);
    } catch (error) {
      const detail = error instanceof Error ? error.message : "Unknown error";
      setMessages((prev) => [...prev, { role: "assistant", content: `I couldn't reach the Orion agent. Check that FastAPI is running on port 8080 and that /ready reports ready. Details: ${detail}` }]);
    } finally { setBusy(false); }
  }

  function submit(e: FormEvent<HTMLFormElement>) { e.preventDefault(); void sendMessage(); }
  function handleKey(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); void sendMessage(); }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#" aria-label="Orion home"><span className="brand-mark">✳</span><span>Orion</span></a>
        <nav className="top-tabs" aria-label="Main sections">
          {["Today", "Find & prioritise", "Reach out"].map((item) => <button key={item} className={tab === item ? "top-tab active" : "top-tab"} onClick={() => setTab(item)}>{item}</button>)}
        </nav>
        <div className="top-right"><span className={`status-dot ${apiStatus}`}></span><span>{apiStatus === "ready" ? "Agent connected" : apiStatus === "offline" ? "Agent offline" : "Connecting…"}</span><button className="avatar" title="Local demo">O</button></div>
      </header>

      <div className="workspace">
        <aside className="sidebar">
          <div className="workspace-label">YOUR WORK</div>
          {[
            ["Today", "◷"], ["Find & prioritise", "⌕"], ["Reach out & keep in contact", "↗"]
          ].map(([label, icon]) => <button key={label} className={tab === label || (label.startsWith("Reach") && tab === "Reach out") ? "side-link selected" : "side-link"} onClick={() => setTab(label === "Reach out & keep in contact" ? "Reach out" : label)}><span>{icon}</span><span>{label}</span></button>)}
          <div className="side-bottom"><div className="side-divider"></div><div className="demo-label">ORION MVP <span>LOCAL DEMO</span></div><p>Illustrative prospect data</p></div>
        </aside>

        <section className="dashboard" aria-label={tab}>
          <div className="page-heading"><div><span className="eyebrow">ORION / YOUR WORK</span><h1>{tab === "Today" ? "Today" : tab}</h1><p>{tab === "Today" ? "A clear view of what deserves your attention." : tab === "Find & prioritise" ? "Promising prospects, ranked by signal strength." : "Keep the next conversation moving."}</p></div><button className="quiet-button" onClick={() => void sendMessage("Give me a concise overview of my highest-priority prospects.")}>Ask Orion <span>↗</span></button></div>
          {tab === "Today" ? <div className="dashboard-grid">
            <section className="panel due-panel"><div className="panel-heading"><div><h2>Worth getting in touch today</h2><span className="count">2</span></div><span className="panel-kicker">FOLLOW UP</span></div>
              <button className="follow-row" onClick={() => void sendMessage("What should I know before calling Quarry Therapeutics?")}><span className="company-avatar purple">QT</span><span className="company-copy"><strong>Quarry Therapeutics</strong><span>They asked you to call in October</span></span><time>2 Oct</time></button>
              <button className="follow-row" onClick={() => void sendMessage("Summarise the context for following up with Alder Pharma.")}><span className="company-avatar blue">AP</span><span className="company-copy"><strong>Alder Pharma</strong><span>Back after summer, as they asked</span></span><time>2 Oct</time></button>
            </section>
            <section className="panel new-panel"><div className="panel-heading"><div><h2>New and worth a look</h2><span className="count">5</span></div><span className="panel-kicker">PRIORITY</span></div>
              {prospects.map((p) => <button key={p.name} className="prospect-row" onClick={() => void sendMessage(`Tell me why ${p.name} is a prospect and what action you recommend.`)}><span className="score"><i></i>{p.score}</span><span className="company-copy"><strong>{p.name}</strong><span>{p.detail}</span></span><span className="row-arrow">↗</span></button>)}
            </section>
            <section className="panel insight-panel"><div className="panel-heading"><div><h2>Your next best move</h2><span className="count">AI INSIGHT</span></div></div><p>Wren has a recent funding signal and no manufacturing partner mentioned in the demo brief.</p><button onClick={() => void sendMessage("Why is Wren Biosciences the strongest new prospect, and what should I do next?")}>Explore this signal <span>→</span></button></section>
            <section className="panel signal-panel"><div className="panel-heading"><div><h2>Pipeline at a glance</h2><span className="count">DEMO DATA</span></div></div><div className="pipeline-stats"><div><strong>10</strong><span>Prospects</span></div><div><strong>3</strong><span>Regions</span></div><div><strong>4</strong><span>Stages</span></div></div><p>Ask Orion to filter by region, risk, industry or stage.</p></section>
          </div> : <section className="panel table-panel"><div className="panel-heading"><div><h2>{tab === "Find & prioritise" ? "Prospects to explore" : "Suggested follow-ups"}</h2><span className="count">{tab === "Find & prioritise" ? "5 MATCHES" : "2 DUE"}</span></div><button className="text-button" onClick={() => void sendMessage(tab === "Find & prioritise" ? "List and rank prospects by opportunity value and risk." : "Help me prepare for my next two follow-up calls.")}>Ask Orion ↗</button></div>{prospects.map((p) => <button key={p.name} className="prospect-detail-row" onClick={() => void sendMessage(`Give me the available details and recommended next step for ${p.name}.`)}><div><strong>{p.name}</strong><span>{p.detail}</span></div><span>{p.region}</span><span>{p.stage}</span><span className={`risk risk-${p.risk.toLowerCase()}`}>{p.risk} risk</span><span className="detail-score">{p.score}</span></button>)}</section>}
          <div className="footnote">Prototype workspace · Synthetic sample companies · Not connected to live customer systems</div>
        </section>

        <aside className="chat-panel">
          <div className="chat-header"><div className="orion-symbol">✳</div><div className="chat-heading"><strong>Orion</strong><span>YOUR PROSPECT ASSISTANT</span></div><button className="about-button" title="About this assistant">About</button><button className="expand-button" title="Expand chat" onClick={() => document.querySelector(".chat-panel")?.classList.toggle("expanded")}>⤢</button></div>
          <div className="conversation">
            <div className="date-label">TUESDAY · YOUR DAILY BRIEF</div>
            {messages.map((m, i) => <div key={i} className={`message message-${m.role}`}><div className="message-avatar">{m.role === "assistant" ? "✳" : "You"}</div><div className="message-body"><div className="message-content">{m.content}</div>{m.tools && m.tools.length > 0 && <div className="tool-trace"><span className="trace-dot"></span> Used {m.tools.join(", ")}</div>}</div></div>)}
            {busy && <div className="message message-assistant"><div className="message-avatar">✳</div><div className="typing"><i></i><i></i><i></i><span>Orion is thinking</span></div></div>}
            <div ref={endRef} />
          </div>
          <div className="chat-compose-area">
            <div className="suggestions">{suggestions.map((s) => <button key={s} onClick={() => void sendMessage(s)} disabled={busy}>{s}</button>)}</div>
            <form className="composer" onSubmit={submit}><textarea value={draft} onChange={(e) => setDraft(e.target.value)} onKeyDown={handleKey} placeholder="Ask or tell Orion…" rows={2} aria-label="Message Orion" disabled={busy}/><button className="send-button" type="submit" disabled={!draft.trim() || busy} aria-label="Send message">↑</button></form>
            <div className="composer-foot"><span>Enter to send · Shift + Enter for a new line</span><span>Local AI</span></div>
          </div>
        </aside>
      </div>
    </main>
  );
}