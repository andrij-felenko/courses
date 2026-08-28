import { describe, it, expect } from "vitest";

const FIXED = "req-TEST";  // кореляційний id нормалізуємо, щоб знімок був стабільний

// по одному зразку на клас; ключ — той самий code, що й у каталозі
const SAMPLES: Record<string, () => DomainError> = {
  device_not_found:   () => new DeviceNotFound("42"),
  device_unavailable: () => new DeviceUnavailable("42"),
  invalid_command:    () => new InvalidCommand("mode", "невідоме значення"),
  rate_limited:       () => new RateLimited(30),
};

describe("контракт помилок DH", () => {
  // (а) інваріанти — над УСІМА класами каталогу, не над рукописним списком
  it("кожен зареєстрований клас дає валідний конверт RFC 9457", () => {
    for (const row of CATALOG.values()) {
      const make = SAMPLES[row.code];
      expect(make, `нема зразка для ${row.code} — додай його`).toBeDefined();
      const p = toProblem(make(), FIXED);
      expect(p.status).toBe(row.status);
      expect(p.body.status).toBe(row.status);              // статус у тілі === HTTP-статус
      expect(p.body.code).toBe(row.code);                  // стабільний ярлик присутній
      expect(p.body.requestId).toBe(FIXED);                // кореляційний id відлунено
      expect(typeof p.body.detail).toBe("string");         // текст Є, але його ЗМІСТ не пришпилюємо
      expect(p.headers["Content-Type"]).toBe("application/problem+json");
      if (row.retryable) expect(p.headers["Retry-After"]).toBeDefined();
    }
  });

  // (б) golden-знімок — точна форма кожного класу; будь-яка зміна червонить CI
  it.each(Object.entries(SAMPLES))("форма %s пришпилена", (_code, make) => {
    expect(toProblem(make(), FIXED)).toMatchSnapshot();
  });

  // (в) редакція: сирий баг НЕ виносить нутрощів назовні
  it("непередбачений виняток → непрозорий 500 без нутрощів", () => {
    const boom = new Error("SQL: SELECT password FROM users WHERE id=1");
    boom.stack = "at db.query (secret.ts:42)\n" + (boom.stack ?? "");
    const p = toProblem(boom, FIXED);                      // прод-режим: expose off
    expect(p.status).toBe(500);
    expect(p.body.code).toBe("internal");
    expect(p.body.requestId).toBe(FIXED);
    expect(p.body).not.toHaveProperty("debug");            // у проді жодного стека
    expect(JSON.stringify(p)).not.toMatch(/SQL|password|secret\.ts|SELECT/);
  });
});
