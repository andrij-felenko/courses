import { gzipSync } from "node:zlib";

// Gzip: якщо клієнт приймає стиснення — стискаємо готове тіло.
const gzip: Middleware = (next) => async (req) => {
  const res = await next(req);
  if (!(req.headers["accept-encoding"] ?? "").includes("gzip")) return res;
  const packed = gzipSync(res.body); // стискаємо вже сформоване тіло
  return {
    ...res,
    headers: { ...res.headers, "content-encoding": "gzip" },
    body: packed.toString("base64"), // у справжньому коді — Buffer на дріт
  };
};

// Recover: НАЙЗОВНІШНІЙ — ловить виняток із будь-якого глибшого шару.
const recover: Middleware = (next) => async (req) => {
  try {
    return await next(req);
  } catch (err) {
    console.error("паніка:", err);
    return { status: 500, headers: {}, body: "internal error" };
  }
};
