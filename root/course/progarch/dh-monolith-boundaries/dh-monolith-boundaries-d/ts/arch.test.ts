// arch.test.ts — виконуваний тест графа (dependency-cruiser / eslint-boundaries)
const ALLOWED: Record<string, Set<string>> = {
  automations: new Set(["twin", "ids", "identity"]),
  billing:     new Set(["ids", "identity"]),        // НЕ control!
  telemetry:   new Set(["ids", "identity"]),        // control знають лише через подію
};
test("жоден модуль не проліз повз двері", () => {
  for (const [mod, deps] of actualImports()) {
    for (const d of deps) expect(ALLOWED[mod]).toContain(d);
  }
});
