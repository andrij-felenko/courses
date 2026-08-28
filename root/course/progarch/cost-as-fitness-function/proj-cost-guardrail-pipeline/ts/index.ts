import * as fs from 'fs';

interface ResourceDiff {
  name: string;
  resourceType: string;
  monthlyCostDiff: string;
}

interface InfracostDiff {
  totalPastMonthlyCost: string;
  totalMonthlyCost: string;
  totalMonthlyCostDiff: string;
  projects: Array<{
    breakdown: {
      resources: ResourceDiff[];
    };
  }>;
}

export function evaluateGuardrailTS(diffPath: string, maxDiffUsd: number = 200.0): boolean {
  const rawData = fs.readFileSync(diffPath, 'utf-8');
  const data: InfracostDiff = JSON.parse(rawData);
  const diffUsd = parseFloat(data.totalMonthlyCostDiff || '0');
  
  if (diffUsd > maxDiffUsd) {
    console.error(`[FinOps Guardrail] Cost increase $${diffUsd} exceeds limit $${maxDiffUsd}`);
    return false;
  }
  
  console.log(`[FinOps Guardrail] Cost check passed: +$${diffUsd}/month`);
  return true;
}
