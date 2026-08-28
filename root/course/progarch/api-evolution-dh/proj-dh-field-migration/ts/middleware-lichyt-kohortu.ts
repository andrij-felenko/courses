function deprecationMiddleware(counter: ReadCounter) {
  return (req: Request, res: Response, next: NextFunction) => {
    const cohort = cohortOf(req);
    const fields = parseFields(req.query.fields);
    const sendJson = res.json.bind(res);

    res.json = (body: unknown) => {
      const projected =
        fields && body && typeof body === "object"
          ? project(body as object, fields)
          : body;

      // Які застарілі поля таки поїхали ЦІЙ відповіді?
      const inPlay = DEPRECATED.filter(
        d => projected != null &&
             Object.prototype.hasOwnProperty.call(projected, d.field),
      );

      for (const dep of inPlay) {
        counter.hit(dep.field, cohort);   // ← поле поїхало когорті: рахуємо як читання
        res.append("Link", `<${dep.docs}>; rel="deprecation"; type="text/html"`);
      }

      if (inPlay.length > 0) {
        // Deprecation/Sunset — на РЕСУРС (RFC 9745 їх означує ресурсними, не польовими),
        // тож беремо найраніше застаріння й найближчий захід сонця з тих, що в грі.
        const dep = Math.min(...inPlay.map(d => d.deprecatedAt));
        const sunset = Math.min(...inPlay.map(d => d.sunsetAt));
        res.setHeader("Deprecation", `@${dep}`);                         // RFC 9745
        res.setHeader("Sunset", new Date(sunset * 1000).toUTCString());  // RFC 8594
        // Щоб CDN не «поглинув» ці читання й не осліпив лічильник (див. пастки):
        res.setHeader("Cache-Control", "private, no-store");
        res.setHeader("Vary", "Api-Version, User-Agent");
      }
      return sendJson(projected);
    };
    next();
  };
}

// Хендлер лишається наївно простим — уся дисципліна в обгортці:
app.get("/devices/:id", deprecationMiddleware(counter), (req, res) => {
  res.json(buildDeviceState(registry.load(req.params.id)));
});
