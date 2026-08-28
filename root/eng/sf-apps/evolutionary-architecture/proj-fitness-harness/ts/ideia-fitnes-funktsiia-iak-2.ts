async function runHarness(ffs: FitnessFunction[]): Promise<number> {
  let failed = 0;
  for (const ff of ffs) {
    const v = await ff.run();            // await не заважає синхронним — вони теж підійдуть
    console.log(`[${v.passed ? "PASS" : "FAIL"}] ${ff.name} — ${ff.axis}\n        ${v.detail}`);
    if (!v.passed) failed++;
  }
  console.log(`\nпідсумок: ${ffs.length - failed}/${ffs.length} осей тримається`);
  return failed === 0 ? 0 : 1;           // код виходу для воріт CI
}
