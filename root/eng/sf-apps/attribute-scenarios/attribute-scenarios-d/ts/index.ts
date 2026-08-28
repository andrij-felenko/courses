function p95(samplesMs: number[]): number {
  const ordered = [...samplesMs].sort((a, b) => a - b);
  // Метод найближчого рангу: індекс, нижче за який лежить 95% значень.
  const k = Math.ceil(0.95 * ordered.length) - 1;
  return ordered[Math.max(k, 0)];
}

function meetsLatencyScenario(samplesMs: number[], thresholdMs: number): boolean {
  // Сценарій: у пік профіль віддається за <= threshold у 95% випадків.
  if (samplesMs.length === 0) return false;   // без даних вимогу не підтверджено
  return p95(samplesMs) <= thresholdMs;
}
