// Express: помічаємо маршрут застарілим
function deprecate(announced: string, sunset: string, docs: string) {
  const depr = `@${Math.floor(Date.parse(announced) / 1000)}`;
  const sun = new Date(sunset).toUTCString();
  return (_req: Request, res: Response, next: NextFunction) => {
    res.setHeader("Deprecation", depr);            // момент оголошення
    res.setHeader("Sunset", sun);                  // момент зняття
    res.setHeader("Link", `<${docs}>; rel="deprecation"; type="text/html"`);
    next();
  };
}
app.get("/v1/orders", deprecate("2024-06-30", "2025-12-31", DOCS), listOrdersV1);
