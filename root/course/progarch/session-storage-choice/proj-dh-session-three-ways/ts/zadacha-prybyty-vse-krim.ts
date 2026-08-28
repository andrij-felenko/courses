import type { Request, Response, NextFunction, RequestHandler } from "express";

function readCredential(req: Request): string {
  const bearer = req.header("authorization")?.replace(/^Bearer /, "");
  return bearer ?? (req as any).cookies?.sid ?? ""; // Bearer (Б/В) або кукі sid (А)
}

// Та сама middleware для ВСІХ трьох варіантів. Міняється лише seam при збірці.
function authenticate(seam: SessionSeam): RequestHandler {
  return async (req: Request, res: Response, next: NextFunction) => {
    const who = await seam.validate(readCredential(req));
    if (!who) return res.status(401).json({ error: "unauthorized" });
    (req as any).principal = who; // далі — лише Principal, походження невидиме
    next();
  };
}

// Викликач — і гадки не має, стор під ним чи підпис. Бачить готового principal.
app.post("/device/:id/unlock", authenticate(seam), (req, res) => {
  const who = (req as any).principal as Principal;
  if (!who.scopes.includes("door:unlock")) return res.status(403).end();
  lock.open(req.params.id, who.home); // ← ось той самий замок вхідних дверей
  res.json({ ok: true });
});
