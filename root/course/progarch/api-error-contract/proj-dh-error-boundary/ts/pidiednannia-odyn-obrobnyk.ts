import { randomUUID } from "node:crypto";
import type { Request, Response, NextFunction } from "express";

function errorBoundary(opts: { exposeInternals: boolean }) {
  return (err: unknown, req: Request, res: Response, _next: NextFunction) => {
    // id призначає ранній middleware на вході; тут лише читаємо той самий,
    // що вже стоїть на КОЖНОМУ рядку журналу цього запиту.
    const reqId = res.locals.reqId ?? req.header("X-Request-Id") ?? randomUUID();
    const { status, headers, body } = toProblem(err, reqId, opts);
    res.set(headers);
    res.set("X-Request-Id", reqId);          // той самий id — і в заголовку, і в тілі, і в лозі
    res.status(status).json(body);
  };
}

// у проді нутрощі закриті; лишити exposeInternals увімкненим у проді — пастка №1
app.use(errorBoundary({ exposeInternals: process.env.NODE_ENV !== "production" }));
