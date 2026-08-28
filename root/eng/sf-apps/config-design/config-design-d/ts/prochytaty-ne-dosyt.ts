function validate(cfg: Config): void {
  const problems: string[] = [];
  if (!cfg.dbUrl) problems.push("DB_URL не задано");
  if (!(cfg.port >= 1 && cfg.port <= 65535))
    problems.push(`port=${cfg.port} поза діапазоном 1..65535`);
  if (!["debug", "info", "warn", "error"].includes(cfg.logLevel))
    problems.push(`невідомий logLevel=${cfg.logLevel}`);
  if (problems.length) {
    // усі помилки разом, а не по одній за запуск
    throw new Error("Конфіг непридатний:\n  " + problems.join("\n  "));
  }
}
