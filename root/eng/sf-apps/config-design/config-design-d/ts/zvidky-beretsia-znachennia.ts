function loadConfig(): Config {
  // 1. Найслабший пласт: типові значення просто в коді
  let cfg: Partial<Config> = { port: 3000, logLevel: "info", dbUrl: "localhost:5432" };

  // 2. Спільний файл — те, що однакове скрізь
  cfg = { ...cfg, ...readYaml("config.yaml") };

  // 3. Файл конкретного середовища перекриває спільний
  const env = process.env.APP_ENV ?? "dev";
  cfg = { ...cfg, ...readYaml(`config.${env}.yaml`) };

  // 4. Змінні середовища сильніші за файли (сюди хмара кладе секрети)
  if (process.env.PORT) cfg.port = Number(process.env.PORT);
  if (process.env.DB_URL) cfg.dbUrl = process.env.DB_URL;

  // 5. Аргумент рядка перебиває все — разове ручне втручання
  cfg = { ...cfg, ...parseCliOverrides() };
  return cfg as Config;
}
