function cohortOf(req: Request): string {
  const v = req.get("Api-Version");                 // "2026-01-10"
  if (v) return `api:${v}`;
  const ua = req.get("User-Agent") ?? "";
  const app = ua.match(/DHApp\/(\d+)\.(\d+)/);        // "DHApp/3.4 (iOS 17)"
  if (app) return `app:${app[1]}.${app[2]}`;
  const panel = ua.match(/DHPanel\/(\d+)/);           // прошивка панелі
  if (panel) return `panel:fw${panel[1]}`;
  return "unknown";                                  // чужі інтеграції, curl, боти
}
