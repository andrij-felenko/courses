const edge = (a: string, b: string) => `${a}->${b}`;

function layerRule(g: Graph, allowed: Set<string>): FitnessFunction {
  return {
    name: "layers",
    axis: "структура: залежності шарів",
    run(): Verdict {
      const bad: string[] = [];
      for (const [from, tos] of g)
        for (const to of tos)
          if (!allowed.has(edge(from, to))) bad.push(`${from} → ${to}`);
      return {
        passed: bad.length === 0,
        detail: bad.length ? `заборонені ребра: ${bad.join(", ")}`
                           : "усі залежності дозволені",
      };
    },
  };
}
