// Компактні конструктори: ключ прояву = "<в'ю>:<назва>".
const M = (view: View, label: string): Manifestation => ({ id: `${view}:${label}`, view, label });
const C = (a: string, b: string): Correspondence => ({ a, b });

const demo: Description = {
  manifestations: [
    M('functional', 'OrderApi'),    M('functional', 'OrderValidator'),
    M('functional', 'PricingEngine'), M('functional', 'AuditLog'),
    M('development', 'order-api'),  M('development', 'order-validation'),
    M('development', 'pricing'),    M('development', 'audit'),
    M('concurrency', 'api-loop'),   M('concurrency', 'order-pool'),
    M('concurrency', 'pricing-pool'),               // ← для AuditLog прояву в конкурентній НЕМАЄ
    M('deployment', 'OrderApi'),    M('deployment', 'OrderValidator'),
    M('deployment', 'PricingEngine'), M('deployment', 'AuditLog'),
    M('information', 'draft-order'),
  ],
  correspondences: [
    C('functional:OrderApi', 'development:order-api'),
    C('functional:OrderApi', 'concurrency:api-loop'),
    C('functional:OrderApi', 'deployment:OrderApi'),
    C('functional:OrderValidator', 'development:order-validation'),
    C('functional:OrderValidator', 'concurrency:order-pool'),
    C('functional:OrderValidator', 'deployment:OrderValidator'),
    C('functional:OrderValidator', 'information:draft-order'),
    C('functional:PricingEngine', 'development:pricing'),
    C('functional:PricingEngine', 'concurrency:pricing-pool'),
    C('functional:PricingEngine', 'deployment:PricingEngine'),
    C('functional:AuditLog', 'development:audit'),
    C('functional:AuditLog', 'deployment:AuditLog'),  // ← конкурентної відповідності немає → сирота
  ],
  deployment: {
    hosts: {
      'deployment:OrderApi': ['svc-api'],
      'deployment:OrderValidator': ['svc-order-1', 'svc-order-2'],   // ← репліки!
      'deployment:PricingEngine': ['svc-pricing'],
      'deployment:AuditLog': ['svc-api'],
    },
    links: [
      ['svc-api', 'svc-order-1'], ['svc-api', 'svc-order-2'],
      ['svc-order-1', 'svc-pricing'], ['svc-order-2', 'svc-pricing'],
    ],
  },
  calls: [
    { from: 'functional:OrderApi', to: 'functional:OrderValidator', kind: 'local' },  // ← БАГ
    { from: 'functional:OrderApi', to: 'functional:AuditLog',       kind: 'local' },  // ← щиро локальний
    { from: 'functional:OrderValidator', to: 'functional:PricingEngine', kind: 'remote' },
  ],
  requiredViews: ['development', 'concurrency', 'deployment'],
};

function run(desc: Description): number {
  const groups = resolveGroups(desc);
  const orphans = checkCoverage(groups, desc.requiredViews);
  const falseLocals = checkFalseLocal(desc, groups);

  for (const o of orphans)
    console.log(`[orphan]       ${o.element} — немає прояву в в'ю: ${o.missing.join(', ')}`);
  for (const f of falseLocals)
    console.log(`[false-local]  ${f.from} → ${f.to} — ${f.why}`);

  const total = orphans.length + falseLocals.length;
  console.log(`consistency: ${total} violation(s)`);
  return total === 0 ? 0 : 1;                          // 0 — пропустити, 1 — завалити збірку
}

process.exit(run(demo));
