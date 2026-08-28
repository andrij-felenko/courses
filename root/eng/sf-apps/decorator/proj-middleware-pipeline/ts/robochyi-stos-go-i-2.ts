// Auth: немає права → 401 і ВИХІД, next не викликаний (обрив ланцюга).
const auth: Middleware = (next) => async (req) => {
  if (!req.headers["authorization"]) {
    return { status: 401, headers: {}, body: "unauthorized" }; // ← next НЕ викликаний
  }
  return next(req);
};

// Cache: на влученні віддаємо збережене й не йдемо глибше; на промаху —
// делегуємо й кладемо відповідь у сховище на майбутнє.
function cache(store: Map<string, Res>): Middleware {
  return (next) => async (req) => {
    if (req.method === "GET") {
      const hit = store.get(req.path);
      if (hit) return { ...hit, headers: { ...hit.headers, "x-cache": "HIT" } }; // ← обрив
    }
    const res = await next(req);
    if (req.method === "GET" && res.status === 200) store.set(req.path, res);     // зберегли
    return res;
  };
}
