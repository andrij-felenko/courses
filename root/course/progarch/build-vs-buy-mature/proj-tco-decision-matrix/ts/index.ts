interface TCOInputOption {
  name: string;
  initialCost: number;
  quarterlyBaseInfra: number;
  sreFteCount: number;
  sreQuarterlySalary: number;
  saasCostPerUnit: number;
  vendorAnnualGrowth: number;
  egressCostPerGb: number;
}

interface TCOSimulationResult {
  totalNpv: number;
  quarterlyBreakdown: number[];
}

function simulateTCO(
  option: TCOInputOption,
  quarterlyUnits: number[],
  quarterlyEgressGb: number[],
  annualDiscountRate: number = 0.08
): TCOSimulationResult {
  if (quarterlyUnits.length !== 12 || quarterlyEgressGb.length !== 12) {
    throw new Error("Simulation requires 12 quarters of data.");
  }

  const quarterlyR = Math.pow(1.0 + annualDiscountRate, 0.25) - 1.0;
  let totalNpv = option.initialCost;
  const quarterlyBreakdown: number[] = [];

  for (let q = 0; q < 12; q++) {
    const year = Math.floor(q / 4);
    const units = quarterlyUnits[q];
    const egress = quarterlyEgressGb[q];

    const vendorMarkup = Math.pow(1.0 + option.vendorAnnualGrowth, year);
    const licenseCost = units * option.saasCostPerUnit * vendorMarkup;
    const opsCost = option.sreFteCount * option.sreQuarterlySalary;
    const egressCost = egress * option.egressCostPerGb;

    const rawCost = licenseCost + opsCost + option.quarterlyBaseInfra + egressCost;
    const discountFactor = Math.pow(1.0 + quarterlyR, q + 1);
    const discounted = rawCost / discountFactor;

    totalNpv += discounted;
    quarterlyBreakdown.push(discounted);
  }

  return { totalNpv, quarterlyBreakdown };
}
