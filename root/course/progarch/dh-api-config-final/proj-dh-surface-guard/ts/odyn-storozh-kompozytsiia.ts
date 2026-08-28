function main(): void {
  const V: Violation[] = [
    ...diffSurface(baseline, describe(SURFACE), loadDeprecated()),
    ...scanConfig(manifest),
    ...loadSamples().flatMap(s => lintError(s).map(reason => ({ path: "error-sample", reason }))),
  ];
  if (V.length === 0) { console.log("✅ поверхня ціла"); return; }
  for (const v of V) console.error(`❌ ${v.path}: ${v.reason}`);
  process.exit(1);                 // ← падіння CI: складання червоне, merge заблоковано
}
