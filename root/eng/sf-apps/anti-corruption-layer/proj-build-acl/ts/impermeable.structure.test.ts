// tests/impermeable.structure.test.ts
// Fitness-функція: жоден файл домену не сміє імпортувати нічого з crm/.
import { readFileSync } from "fs";
import { globSync } from "glob";

test("домен не імпортує CRM", () => {
  const domainFiles = globSync("src/domain/**/*.ts");
  const offenders: string[] = [];

  for (const file of domainFiles) {
    const src = readFileSync(file, "utf8");
    // будь-який import ... from "...crm..." — порушення
    const importsCrm = /import[^;]*from\s+["'][^"']*\/crm\/[^"']*["']/.test(src);
    if (importsCrm) offenders.push(file);
  }

  expect(offenders).toEqual([]); // жодного протікання на рівні залежностей
});
