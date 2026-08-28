async function main(): Promise<void> {
  const g = buildGraph("src");                                  // спільна основа для двох осей

  const allowed = new Set(["ui->domain", "domain->ports", "db->ports"]);
  const b: Budget = { maxP95Ms: 200, maxArtifactKb: 250 };      // бюджети зі сценаріїв

  const ffs: FitnessFunction[] = [
    layerRule(g, allowed),        // вісь структури  (атомарна)
    acyclic(g),                   // вісь форми графа (атомарна)
    budget(measureLive, b),       // осі швидкодії й постачання (цілісна)
  ];

  process.exit(await runHarness(ffs));                          // 0 пропускає, 1 валить конвеєр
}
main();
