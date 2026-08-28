function report(sync: Violation[], overdue: Violation[]): number {
  const show = (title: string, vs: Violation[]) => {
    console.log(`\n${title}`);
    if (!vs.length) { console.log("  чисто"); return; }
    for (const v of vs) console.log(`  ✗ ${v.id.padEnd(7)} ${v.detail}`);
  };
  show("СИНХРОНІЗАЦІЯ КОД ↔ ЖУРНАЛ", sync);
  show("СТРОКИ (тригер проти знімка метрик)", overdue);
  const n = sync.length + overdue.length;
  console.log(n ? `\n${n} порушень → борг вийшов з-під контролю, CI падає`
                : "\nборг під контролем — CI зелений");
  return n ? 1 : 0;
}

// У CI:  const markers = scanMarkers("src");  const metrics = readSnapshot();
// Тут — відтворюваний знімок того, що вони повернули б.
const MARKERS: Marker[] = [
  { id: "DH-014", at: "panel/energy.ts:42" }, { id: "DH-031", at: "export/report.ts:17" },
  { id: "DH-022", at: "panel/energy.ts:31" }, { id: "DH-007", at: "panel/legacy.ts:88" },
];
const METRICS = { panel_p95_ms: 930, max_devices_per_home: 4200, rule_types: 4 };

process.exit(report(checkSync(MARKERS, JOURNAL), checkOverdue(JOURNAL, METRICS)));
