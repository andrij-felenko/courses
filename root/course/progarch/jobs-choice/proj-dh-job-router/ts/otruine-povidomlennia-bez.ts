const sys = makeSystem();
for (let i = 0; i < 4; i++)
  sys.broker.put({ cls: "notify", key: `n-${i}`, payload: { i } });

const processed = new Set<string>();
let attempts = 0;
sys.broker.deliver("notify", (job) => {
  attempts++;
  if ((job.payload as { i: number }).i === 2) throw new Error("otruta: несправний payload");
  if (processed.has(job.key)) return;                 // ідемпотентність: дубль — нічого
  processed.add(job.key);
});
console.log("оброблено:", processed.size, " спроб:", attempts, " DLQ:", sys.broker.dlq.length);
