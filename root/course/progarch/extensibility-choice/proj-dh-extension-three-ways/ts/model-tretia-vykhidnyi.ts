type Subscriber = { url: string; secret: string };

async function postWithTimeout(url: string, body: unknown, ms: number): Promise<void> {
  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(), ms);    // мертвий одержувач не висить вічно
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
      signal: ctl.signal,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
  } finally {
    clearTimeout(timer);
  }
}

async function dispatch(subs: Subscriber[], ev: MotionEvent): Promise<void> {
  // назовні йде ЛИШЕ те, що ми свідомо поклали — ні токена, ні нутрощів
  const payload = { type: "motion.detected", room: ev.room, at: ev.at };
  const results = await Promise.allSettled(
    subs.map((s) => postWithTimeout(s.url, payload, 800)),
  );
  results.forEach((r, i) => {
    if (r.status === "rejected")
      log.warn(`вебхук ${subs[i].url} впав:`, r.reason);   // один мертвий — решта доставлена
  });
}
