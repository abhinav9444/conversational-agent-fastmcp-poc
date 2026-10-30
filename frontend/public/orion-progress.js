(() => {
  if (window.__orionProgressEnhancementLoaded) return;
  window.__orionProgressEnhancementLoaded = true;

  const phrases = [
    "Thinking through your request",
    "Connecting the relevant details",
    "Working through the possibilities",
    "Preparing a clear answer"
  ];

  const style = document.createElement("style");
  style.textContent = `
    .orion-progress-copy {
      display: inline-block !important;
      color: transparent !important;
      background: linear-gradient(100deg, #7482a5 8%, #a68cf5 32%, #ffffff 50%, #a68cf5 68%, #7482a5 92%) !important;
      background-size: 240% 100% !important;
      background-clip: text !important;
      -webkit-background-clip: text !important;
      -webkit-text-fill-color: transparent !important;
      animation: orion-progress-shimmer 2s linear infinite !important;
      font-style: normal !important;
      font-weight: 600 !important;
      letter-spacing: .01em;
    }
    @keyframes orion-progress-shimmer {
      from { background-position: 120% center; }
      to { background-position: -140% center; }
    }
    @media (prefers-reduced-motion: reduce) {
      .orion-progress-copy { animation: none !important; background-position: center !important; }
    }
  `;
  (document.head || document.documentElement).appendChild(style);

  let phraseIndex = 0;
  let rotation = null;

  function findThinkingElements() {
    return Array.from(document.body.querySelectorAll("*")).filter((element) => {
      if (element.classList.contains("orion-progress-copy")) return false;
      const text = (element.textContent || "").replace(/\s+/g, " ").trim();
      if (!/^thinking(?:…|\.{3})?$/i.test(text)) return false;
      return !Array.from(element.children).some((child) =>
        /^thinking(?:…|\.{3})?$/i.test((child.textContent || "").replace(/\s+/g, " ").trim())
      );
    });
  }

  function startRotation() {
    if (rotation) return;
    rotation = window.setInterval(() => {
      const active = document.querySelectorAll(".orion-progress-copy");
      if (!active.length) {
        window.clearInterval(rotation);
        rotation = null;
        phraseIndex = 0;
        return;
      }
      phraseIndex = (phraseIndex + 1) % phrases.length;
      active.forEach((node) => {
        node.textContent = phrases[phraseIndex] + "…";
      });
    }, 1800);
  }

  function enhanceThinkingText() {
    findThinkingElements().forEach((element) => {
      const progress = document.createElement("span");
      progress.className = "orion-progress-copy";
      progress.setAttribute("role", "status");
      progress.setAttribute("aria-live", "polite");
      progress.textContent = phrases[phraseIndex] + "…";
      element.replaceChildren(progress);
      element.classList.add("orion-progress-host");
      startRotation();
    });
  }

  const observer = new MutationObserver(enhanceThinkingText);
  observer.observe(document.documentElement, {
    childList: true,
    characterData: true,
    subtree: true
  });
  enhanceThinkingText();
})();