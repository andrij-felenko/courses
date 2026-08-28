interface Reading { p95Ms: number; artifactKb: number; }    // обидві величини з ОДНОГО артефакту
interface Budget  { maxP95Ms: number; maxArtifactKb: number; }

function budget(measure: () => Promise<Reading>, b: Budget): FitnessFunction {
  return {
    name: "budget",
    axis: "швидкодія + постачання: час відповіді й розмір разом",
    async run(): Promise<Verdict> {
      const r = await measure();                              // один прогін — обидві величини разом
      const over: string[] = [];
      if (r.p95Ms > b.maxP95Ms)          over.push(`p95 ${r.p95Ms}мс > ${b.maxP95Ms}мс`);
      if (r.artifactKb > b.maxArtifactKb) over.push(`артефакт ${r.artifactKb}КБ > ${b.maxArtifactKb}КБ`);
      return {
        passed: over.length === 0,                            // тримаються ОБИДВА бюджети — чи жодного розміну
        detail: over.length ? over.join("; ") : "обидва бюджети витримано",
      };
    },
  };
}
