"use client";

const PROGRESS_PHRASES = [
  "Thinking through your request",
  "Connecting the relevant details",
  "Working through the possibilities",
  "Preparing a clear answer",
];

function installProgressEnhancement(frame: HTMLIFrameElement | null) {
  const doc = frame?.contentDocument;
  if (!doc?.head || !doc.body || frame.dataset.progressObserverInstalled === "true") return;

  frame.dataset.progressObserverInstalled = "true";

  const style = doc.createElement("style");
  style.id = "orion-live-progress-styles";
  style.textContent = `
    /* Target the exact pending element created by Orion's chat renderer. */
    .orion-chat-pending {
      display: inline-block !important;
      color: transparent !important;
      font-style: normal !important;
      font-weight: 600 !important;
      background-image: linear-gradient(
        90deg,
        #7885a8 0%,
        #9d8be8 24%,
        #ffffff 48%,
        #a58bf4 62%,
        #7885a8 100%
      ) !important;
      background-size: 250% 100% !important;
      background-position: 180% center;
      background-clip: text !important;
      -webkit-background-clip: text !important;
      -webkit-text-fill-color: transparent !important;
      animation: orion-progress-left-to-right 1.8s linear infinite !important;
    }

    @keyframes orion-progress-left-to-right {
      from { background-position: 180% center; }
      to { background-position: -80% center; }
    }

    @media (prefers-reduced-motion: reduce) {
      .orion-chat-pending {
        animation: none !important;
        background-position: center !important;
      }
    }
  `;
  doc.head.appendChild(style);

  let phraseIndex = 0;

  const updatePendingNodes = () => {
    const pending = doc.querySelectorAll<HTMLElement>(".orion-chat-pending");
    pending.forEach((node) => {
      if (node.dataset.progressEnhanced !== "true") {
        node.dataset.progressEnhanced = "true";
        node.textContent = PROGRESS_PHRASES[phraseIndex] + "…";
      }
    });
  };

  // The original V13 renderer replaces the chat markup with ax.innerHTML.
  // Observe that iframe document and re-apply the phrase to each new pending node.
  const observer = new MutationObserver(updatePendingNodes);
  observer.observe(doc.body, {
    childList: true,
    characterData: true,
    subtree: true,
  });

  updatePendingNodes();

  window.setInterval(() => {
    phraseIndex = (phraseIndex + 1) % PROGRESS_PHRASES.length;
    doc.querySelectorAll<HTMLElement>(".orion-chat-pending").forEach((node) => {
      node.textContent = PROGRESS_PHRASES[phraseIndex] + "…";
    });
  }, 1800);
}

export default function HomePage() {
  return (
    <main style={{ width: "100vw", height: "100dvh", overflow: "hidden" }}>
      <iframe
        title="Orion Version 13"
        src="/orion-v13.html"
        onLoad={(event) => installProgressEnhancement(event.currentTarget)}
        style={{ display: "block", width: "100%", height: "100%", border: 0 }}
      />
    </main>
  );
}
