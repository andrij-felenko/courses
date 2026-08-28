import http from 'k6/http';
import { check } from 'k6';

export const options = {
  scenarios: {
    unit_cost_profile: {
      executor: 'shared-iterations',
      vus: 10,
      iterations: 1000,
      maxDuration: '2m',
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<200'], // Latency SLO < 200ms
  },
};

// Вартісні коефіцієнти AWS Lambda / Fargate (USD за одиницю)
const PRICE_PER_CPU_MS = 0.00000001;
const PRICE_PER_RAM_MB_SEC = 0.000000002;

export default function () {
  const res = http.get('http://telemetry-service.staging.local/api/v1/devices/status');
  
  check(res, {
    'status is 200': (r) => r.status === 200,
  });
}

export function handleSummary(data) {
  const avgDurationMs = data.metrics.http_req_duration.values.avg;
  const totalReqs = data.metrics.http_reqs.values.count;
  
  // Оціночний розрахунок юніт-вартості 1000 запитів
  const estimatedCpuCost = avgDurationMs * PRICE_PER_CPU_MS * totalReqs;
  const estimatedRamCost = (256) * (avgDurationMs / 1000) * PRICE_PER_RAM_MB_SEC * totalReqs;
  const totalUnitCostPer1k = estimatedCpuCost + estimatedRamCost;

  return {
    'stdout': textSummary(data, totalUnitCostPer1k),
    '/tmp/k6-unit-cost.json': JSON.stringify({
      total_requests: totalReqs,
      avg_duration_ms: avgDurationMs,
      unit_cost_per_1k_usd: totalUnitCostPer1k
    }),
  };
}

function textSummary(data, unitCost) {
  return `\n========================================\n` +
         `📊 FinOps Dynamic Unit-Cost Summary\n` +
         `----------------------------------------\n` +
         `Всього запитів: ${data.metrics.http_reqs.values.count}\n` +
         `Середній час відгуку: ${data.metrics.http_req_duration.values.avg.toFixed(2)} ms\n` +
         `Юніт-вартість 1000 запитів: $${unitCost.toFixed(6)} USD\n` +
         `========================================\n`;
}
