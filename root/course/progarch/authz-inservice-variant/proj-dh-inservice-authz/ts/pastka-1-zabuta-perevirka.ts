// Чок-пойнт: маршрут РЕЄСТРУЮТЬ лише через guard — повз перевірку його не додаси.
function guard<R extends Resource>(
  action: Action,
  load: (req: Request) => Promise<R>,
  handle: (req: Request, res: Response, resource: R) => Promise<void>,
) {
  return async (req: Request, res: Response) => {
    const resource = await load(req);
    if (!(await authz.can(req.user, action, resource))) {
      return res.status(403).json({ error: "forbidden" });
    }
    await handle(req, res, resource);   // до сюди доходять лише дозволені
  };
}

// Реєстрація: перевірка — не рядок усередині, а обов'язкова частина оголошення маршруту.
router.post("/doors/:id/unlock",
  guard("unlock",
        (req) => devices.load(req.params.id),
        (_req, res, door) => door.unlock().then(() => res.json({ ok: true }))));
