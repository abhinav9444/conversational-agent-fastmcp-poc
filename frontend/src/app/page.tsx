"use client";

function installProgressEnhancement(frame: HTMLIFrameElement | null) {
  const document = frame?.contentDocument;
  if (!document?.head || document.getElementById("orion-progress-enhancement")) return;

  const script = document.createElement("script");
  script.id = "orion-progress-enhancement";
  script.src = "/orion-progress.js?v=2";
  script.async = true;
  document.head.appendChild(script);
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
