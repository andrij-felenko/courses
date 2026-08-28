// decide.test.ts
import { describe, it, expect } from "vitest";
import { decide, type Reading, type Config, type Command } from "./home";

const CFG: Config = { threshold: 20.0 };
const R = (celsius: number, ok = true): Reading => ({ celsius, ok });

describe("decide покриває кожну гілку", () => {
  const cases: Array<[Reading, Command]> = [
    [R(5.0),         "HEAT"],   // глибокий холод
    [R(19.0),        "HEAT"],   // нижче порога
    [R(19.999),      "HEAT"],   // на волосину нижче
    [R(20.0),        "IDLE"],   // рівно на порозі
    [R(20.001),      "IDLE"],   // на волосину вище
    [R(25.0),        "IDLE"],   // тепло
    [R(5.0,  false), "IDLE"],   // холод, але давач мовчить
    [R(25.0, false), "IDLE"],   // тепло, і давач мовчить
  ];
  it.each(cases)("decide(%o) → %s", (r, expected) => {
    expect(decide(r, CFG)).toBe(expected);
  });
});
