function acyclic(g: Graph): FitnessFunction {
  return {
    name: "acyclic",
    axis: "форма графа: шари утворюють DAG",
    run(): Verdict {
      const cycles = findCycles(g);
      return {
        passed: cycles.length === 0,
        detail: cycles.length
          ? cycles.map(c => [...c, c[0]].join(" → ")).join("; ")   // замкнути коло у звіті
          : "граф ациклічний — DAG тримається",
      };
    },
  };
}
