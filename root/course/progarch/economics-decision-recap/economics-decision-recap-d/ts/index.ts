// Обчислення синтетичної вартості ендпойнта у CI/CD
const cpuCostUsd = usage.cpuMs * pricing.costPerCpuMs;
const dbCostUsd = usage.dbQueries * pricing.costPerDbQuery;
const egressCostUsd = (usage.egressBytes / 1e9) * pricing.costPerEgressGb;

const singleRequestCost = cpuCostUsd + dbCostUsd + egressCostUsd;
const unitCostPerK = singleRequestCost * 1000;

if (unitCostPerK > budget.maxUnitCostUsd) {
  throw new Error(`[COST GUARD FAIL] Unit cost $${unitCostPerK.toFixed(4)}/1k перевищує бюджет!`);
}
