// config.ts — єдине місце, де застосунок торкається середовища.
class MissingConfig extends Error {}

function require(name: string): string {
  const value = process.env[name];
  if (!value) throw new MissingConfig(`немає обов'язкової змінної середовища ${name}`);
  return value;
}

function optional(name: string, fallback: string): string {
  return process.env[name] || fallback;
}

export const config = {
  DATABASE_URL: require("DATABASE_URL"),
  SECRET_KEY:   require("SECRET_KEY"),
  PORT:         Number(optional("PORT", "8000")),
  LOG_LEVEL:    optional("LOG_LEVEL", "info"),
} as const;
// Модуль обчислюється при першому import — тобто при старті процесу.
// Бракує обов'язкового — застосунок кидає на старті й не приймає жодного запиту.
