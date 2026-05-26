(function () {
  const ICONS = {
    home: '<path d="m3 10 9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M9 20v-6h6v6"/>',
    store: '<path d="M4 10h16"/><path d="M5 10l1-6h12l1 6"/><path d="M6 10v10h12V10"/><path d="M9 20v-6h6v6"/>',
    truck: '<path d="M3 7h11v10H3z"/><path d="M14 10h4l3 3v4h-7z"/><circle cx="7" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>',
    user: '<circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 14.5-4 16 0"/>',
    wallet: '<path d="M4 7h16v12H4z"/><path d="M4 9l13-4v4"/><path d="M16 13h4"/><circle cx="17" cy="13" r="1"/>',
    card: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 10h18"/><path d="M7 15h4"/>',
    refresh: '<path d="M21 12a9 9 0 0 1-15.5 6.2"/><path d="M3 12A9 9 0 0 1 18.5 5.8"/><path d="M18 2v4h4"/><path d="M6 22v-4H2"/>',
    forecast: '<path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 5-7"/><path d="M19 7h-4V3"/>',
    chat: '<path d="M21 12a8 8 0 0 1-8 8H7l-4 3v-6a8 8 0 1 1 18-5Z"/>',
    logout: '<path d="M10 17l5-5-5-5"/><path d="M15 12H3"/><path d="M21 3v18h-8"/>',
    dashboard: '<rect x="3" y="3" width="7" height="8" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="15" width="7" height="6" rx="1"/>',
    bell: '<path d="M18 8a6 6 0 1 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9"/><path d="M10 21h4"/>',
    package: '<path d="m12 3 8 4.5v9L12 21l-8-4.5v-9L12 3Z"/><path d="m4 7.5 8 4.5 8-4.5"/><path d="M12 12v9"/>',
    trendUp: '<path d="M3 17 9 11l4 4 8-8"/><path d="M14 7h7v7"/>',
    trendDown: '<path d="M3 7l6 6 4-4 8 8"/><path d="M14 17h7v-7"/>',
    pie: '<path d="M21 12A9 9 0 1 1 12 3v9Z"/><path d="M12 3a9 9 0 0 1 9 9h-9Z"/>',
    zap: '<path d="M13 2 3 14h8l-1 8 10-12h-8l1-8Z"/>',
    calculator: '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 7h8"/><path d="M8 11h.01M12 11h.01M16 11h.01M8 15h.01M12 15h.01M16 15h.01"/>',
    map: '<path d="m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3V6Z"/><path d="M9 3v15"/><path d="M15 6v15"/>',
    alert: '<path d="M12 3 2 21h20L12 3Z"/><path d="M12 9v5"/><path d="M12 17h.01"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    check: '<circle cx="12" cy="12" r="9"/><path d="m8 12 3 3 5-6"/>',
    x: '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
    circleX: '<circle cx="12" cy="12" r="9"/><path d="M15 9 9 15"/><path d="m9 9 6 6"/>',
    trophy: '<path d="M8 21h8"/><path d="M12 17v4"/><path d="M7 4h10v5a5 5 0 0 1-10 0V4Z"/><path d="M5 5H3v2a4 4 0 0 0 4 4"/><path d="M19 5h2v2a4 4 0 0 1-4 4"/>',
    factory: '<path d="M3 21h18"/><path d="M5 21V9l5 3V9l5 3V5h4v16"/><path d="M9 17h1M13 17h1M17 17h1"/>',
    send: '<path d="m22 2-7 20-4-9-9-4 20-7Z"/><path d="M22 2 11 13"/>',
    clipboard: '<path d="M9 4h6l1 2h3v15H5V6h3l1-2Z"/><path d="M9 12h6"/><path d="M9 16h6"/>',
    mail: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    lock: '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
    key: '<circle cx="7" cy="14" r="4"/><path d="M11 14h10"/><path d="M17 14v3"/><path d="M20 14v2"/>',
    crown: '<path d="m3 8 4 9h10l4-9-5 3-4-7-4 7-5-3Z"/><path d="M7 21h10"/>',
    handshake: '<path d="M8 12 4 16l4 4 4-4"/><path d="m12 16 4 4 4-4-4-4"/><path d="M8 12l4-4 4 4"/><path d="M2 12l4-4"/><path d="m22 12-4-4"/>',
    bot: '<rect x="5" y="8" width="14" height="10" rx="2"/><path d="M12 8V4"/><circle cx="9" cy="13" r="1"/><circle cx="15" cy="13" r="1"/><path d="M9 17h6"/>',
    pin: '<path d="M12 21s7-5 7-12a7 7 0 1 0-14 0c0 7 7 12 7 12Z"/><circle cx="12" cy="9" r="2"/>',
    inbox: '<path d="M3 13h5l2 3h4l2-3h5"/><path d="M5 4h14l2 9v7H3v-7l2-9Z"/>',
    list: '<path d="M8 6h13M8 12h13M8 18h13"/><path d="M3 6h.01M3 12h.01M3 18h.01"/>',
    settings: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.8 1.8 0 0 0 .4 2l.1.1-2 3.4-.2-.1a1.8 1.8 0 0 0-2 .4l-.2.2h-4l-.2-.2a1.8 1.8 0 0 0-2-.4l-.2.1-2-3.4.1-.1a1.8 1.8 0 0 0 .4-2l-.1-.3-3.5-2v-4l3.5-2 .1-.3a1.8 1.8 0 0 0-.4-2l-.1-.1 2-3.4.2.1a1.8 1.8 0 0 0 2-.4l.2-.2h4l.2.2a1.8 1.8 0 0 0 2 .4l.2-.1 2 3.4-.1.1a1.8 1.8 0 0 0-.4 2l.1.3 3.5 2v4l-3.5 2-.1.3Z"/>',
    shield: '<path d="M12 3 5 6v6c0 5 3.5 8 7 9 3.5-1 7-4 7-9V6l-7-3Z"/><path d="m9 12 2 2 4-5"/>',
    gem: '<path d="M6 3h12l4 6-10 12L2 9l4-6Z"/><path d="M2 9h20"/><path d="m8 9 4 12 4-12"/>',
    pencil: '<path d="M16 3l5 5L8 21H3v-5L16 3Z"/><path d="m15 5 4 4"/>',
    tag: '<path d="M20 10 12 2H4v8l8 8 8-8Z"/><circle cx="8" cy="6" r="1"/>',
    target: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    arrowRight: '<path d="M5 12h14"/><path d="m13 6 6 6-6 6"/>',
    hourglass: '<path d="M6 2h12"/><path d="M6 22h12"/><path d="M7 2c0 5 5 6 5 10s-5 5-5 10"/><path d="M17 2c0 5-5 6-5 10s5 5 5 10"/>',
    cart: '<circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>',
    users: '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    plus: '<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>',
    wrench: '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
    rocket: '<path d="M22 2c0 0-4.5 1.1-8 5.5s-4 9-4 9L5 22l-3-3 5.5-5s4.5-.5 9-4 5.5-8 5.5-8zM14 10l-4-4M9 15l-3-3"/>',
    building: '<rect x="4" y="2" width="16" height="20" rx="2"/><path d="M9 22v-6h6v6M9 6h6M9 10h6M9 14h6"/>',
    power: '<path d="M18.36 6.64a9 9 0 1 1-12.73 0M12 2v10"/>',
    phone: '<rect x="5" y="2" width="14" height="20" rx="2"/><path d="M12 18h.01"/>',
    sparkles: '<path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>'
  };

  const GLYPH_ICON = new Map([
    ['🏠', 'home'], ['🏪', 'store'], ['🚚', 'truck'], ['🧑', 'user'], ['💼', 'user'],
    ['💰', 'wallet'], ['💳', 'card'], ['🔄', 'refresh'], ['🔮', 'forecast'], ['💬', 'chat'],
    ['🚪', 'logout'], ['📊', 'dashboard'], ['🔔', 'bell'], ['📦', 'package'], ['📈', 'trendUp'],
    ['🍩', 'pie'], ['⚡', 'zap'], ['🧮', 'calculator'], ['🗺', 'map'], ['🚨', 'alert'],
    ['🕐', 'clock'], ['✅', 'check'], ['⚠', 'alert'], ['🐢', 'hourglass'], ['🏆', 'trophy'],
    ['🏭', 'factory'], ['➤', 'send'], ['📋', 'clipboard'], ['✕', 'x'], ['❌', 'circleX'],
    ['✉', 'mail'], ['🔒', 'lock'], ['🔑', 'key'], ['👑', 'crown'], ['🤝', 'handshake'],
    ['🤖', 'bot'], ['📍', 'pin'], ['📩', 'inbox'], ['🔢', 'list'], ['⚙', 'settings'],
    ['🛡', 'shield'], ['💎', 'gem'], ['✏', 'pencil'], ['🏷', 'tag'], ['🎯', 'target'],
    ['↑', 'trendUp'], ['↓', 'trendDown'], ['→', 'arrowRight'], ['⏳', 'hourglass'],
    ['🛍', 'cart'], ['👤', 'user'], ['🔌', 'power'], ['➕', 'plus'], ['🛒', 'cart'],
    ['🏢', 'building'], ['👥', 'users'], ['📱', 'phone'], ['📥', 'inbox'], ['📤', 'send'],
    ['🛠', 'wrench'], ['🚀', 'rocket'], ['✨', 'sparkles'], ['💸', 'wallet']
  ]);
  const EMOJI_RE = /[\p{Extended_Pictographic}\u2190-\u21ff\u2300-\u23ff\u2600-\u27bf]\uFE0F?/gu;

  function svg(name) {
    const paths = ICONS[name] || ICONS.dashboard;
    return `<span class="dp-icon" aria-hidden="true"><svg viewBox="0 0 24 24">${paths}</svg></span>`;
  }

  function pickIconFromText(text) {
    for (const [glyph, name] of GLYPH_ICON.entries()) {
      if (text.includes(glyph)) return name;
    }
    if (/dashboard|overview/i.test(text)) return 'dashboard';
    if (/retailer|store/i.test(text)) return 'store';
    if (/distributor/i.test(text)) return 'truck';
    if (/salesperson|salesperson/i.test(text)) return 'user';
    if (/money|revenue|sale|cash|finance/i.test(text)) return 'wallet';
    if (/credit|payment/i.test(text)) return 'card';
    if (/forecast|demand|ai/i.test(text)) return 'forecast';
    if (/communication|message|channel/i.test(text)) return 'chat';
    if (/stock|product|inventory/i.test(text)) return 'package';
    if (/alert|warning|overdue/i.test(text)) return 'alert';
    if (/history|recent|activity/i.test(text)) return 'clock';
    if (/calculate|split/i.test(text)) return 'calculator';
    if (/save|record|add/i.test(text)) return 'check';
    if (/send/i.test(text)) return 'send';
    if (/sign out|logout/i.test(text)) return 'logout';
    if (/sign in/i.test(text)) return 'arrowRight';
    return null;
  }

  function cleanText(node) {
    node.nodeValue = node.nodeValue.replace(EMOJI_RE, '').replace(/\s{2,}/g, ' ');
  }

  function prependIcon(el, name) {
    if (!name || el.querySelector(':scope > .dp-icon')) return;
    el.insertAdjacentHTML('afterbegin', svg(name));
    if (el.firstChild && el.firstChild.nextSibling && el.firstChild.nextSibling.nodeType === Node.TEXT_NODE) {
      el.firstChild.nextSibling.nodeValue = ' ' + el.firstChild.nextSibling.nodeValue.trimStart();
    }
  }

  function iconizeElement(el) {
    const original = el.textContent || '';
    const name = pickIconFromText(original);
    if (el.classList.contains('nav-icon') || el.classList.contains('kpi-icon') || el.classList.contains('fi-icon') || el.classList.contains('inp-icon')) {
      el.innerHTML = name ? svg(name) : '';
      return;
    }
    if (el.classList.contains('notif-btn')) {
      el.childNodes.forEach((node) => { if (node.nodeType === Node.TEXT_NODE) cleanText(node); });
      prependIcon(el, 'bell');
      return;
    }
    if (name && /[\p{Extended_Pictographic}\u2190-\u21ff\u2300-\u23ff\u2600-\u27bf]/u.test(original)) {
      prependIcon(el, name);
    }
  }

  function cleanTree(root) {
    root.querySelectorAll('.nav-icon,.kpi-icon,.fi-icon,.inp-icon,.notif-btn,.topbar-title,.chart-title,.btn,.qa-btn,.channel-tab,.login-title,.brand-badge,.feature-item,.alert-item,.badge,.toast span,.msg-time').forEach(iconizeElement);
    root.querySelectorAll('a,button,div,span').forEach((el) => {
      if (el.querySelector(':scope > .dp-icon')) return;
      const directText = Array.from(el.childNodes)
        .filter((node) => node.nodeType === Node.TEXT_NODE)
        .map((node) => node.nodeValue)
        .join(' ');
      EMOJI_RE.lastIndex = 0;
      if (EMOJI_RE.test(directText)) iconizeElement(el);
    });

    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        EMOJI_RE.lastIndex = 0;
        if (!EMOJI_RE.test(node.nodeValue)) return NodeFilter.FILTER_REJECT;
        EMOJI_RE.lastIndex = 0;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    const textNodes = [];
    while (walker.nextNode()) textNodes.push(walker.currentNode);
    textNodes.forEach(cleanText);
  }

  window.DPIcons = { svg, cleanTree };

  document.addEventListener('DOMContentLoaded', () => {
    cleanTree(document.body);
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) cleanTree(node);
          if (node.nodeType === Node.TEXT_NODE) cleanText(node);
        });
      });
    });
    observer.observe(document.body, { childList: true, subtree: true });
  });
}());
