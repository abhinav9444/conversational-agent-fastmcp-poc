(() => {
  if (window.__orionProgressEnhancementLoaded) return;
  window.__orionProgressEnhancementLoaded = true;

  const phrases = [
    "Thinking through your request",
    "Connecting the relevant details",
    "Working through the possibilities",
    "Putting the answer together"
  ];
  const style = document.createElement("style");
  style.textContent = `
    .orion-progress-copy {
      display: inline-block;
      color: transparent !important;
      background: linear-gradient(100deg, #7783a5 10%, #b39aff 35%, #ffffff 50%, #9c83f4 65%, #7783a5 90%);
      background-size: 220% auto;
      background-clip: text;
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      animation: orion-progress-shimmer 2.2s linear infinite;
      font-weight: 500;
      letter-spacing: .01em;
    }
    @keyframes orion-progress-shimmer {
      to { background-position: -220% center; }
    }
    @media (prefers-reduced-motion: reduce) {
      .orion-progress-copy { animation: none; background-position: center; }
    }
  `;
  (document.head || document.documentElement).appendChild(style);

  let phraseIndex = 0;
  let rotation = null;

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
    }, 1900);
  }

  function enhanceThinkingText() {
    const walker = document.createTreeWalker(
      document.body,
      NodeFilter.SHOW_TEXT
    );
    const candidates = [];
    while (walker.nextNode()) {
      const node = walker.currentNode;
      if (/^thinking(?:…|\.{3})?$/i.test((node.nodeValue || "").trim())) {
        candidates.push(node);
      }
    }

    candidates.forEach((node) => {
      const parent = node.parentElement;
      if (!parent || parent.closest(".orion-progress-copy")) return;
      const progress = document.createElement("span");
      progress.className = "orion-progress-copy";
      progress.setAttribute("role", "status");
      progress.setAttribute("aria-live", "polite");
      progress.textContent = phrases[phraseIndex] + "…";
      node.parentNode.replaceChild(progress, node);
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