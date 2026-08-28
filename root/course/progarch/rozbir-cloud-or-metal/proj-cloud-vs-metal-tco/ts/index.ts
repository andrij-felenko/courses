export interface WorkloadRequirements {
  vCpuNeeded: number;
  ramGbNeeded: number;
  storageTbNeeded: number;
  monthlyEgressGb: number;
  horizonMonths: number;
}

export interface CloudPricing {
  pricePerVcpuHour: number;
  pricePerRamGbHour: number;
  storagePricePerTbMonth: number;
  egressPricePerGb: number;
  managedServicesFeeMonthly: number;
}

export interface BareMetalPricing {
  serverCapEx: number;             // вартість одного сервера (CapEx)
  vCpuPerServer: number;
  ramGbPerServer: number;
  storageTbPerServer: number;
  rackUnitMonthlyFee: number;       // оренда юніта в ЦОД
  powerKwPerHourPrice: number;       // вартість кВт·год
  serverPowerDrawKw: number;        // споживання одного сервера в кВт
  pueRatio: number;                 // коефіцієнт PUE (наприклад 1.25)
  unmeteredBandwidthMonthlyFee: number; // плоский 10G порт
  opsSalaryAllocationMonthly: number; // частка зарплати інженера
}

export interface TcoComparisonResult {
  cloudMonthlyTotal: number;
  bareMetalMonthlyTotal: number;
  bareMetalCapExTotal: number;
  monthlySavings: number;
  paybackPeriodMonths: number;
}

export function calculateTco(
  req: WorkloadRequirements,
  cloud: CloudPricing,
  metal: BareMetalPricing
): TcoComparisonResult {
  const hoursPerMonth = 730;

  // 1. Хмарні витрати
  const cloudCompute = req.vCpuNeeded * cloud.pricePerVcpuHour * hoursPerMonth +
                       req.ramGbNeeded * cloud.pricePerRamGbHour * hoursPerMonth;
  const cloudStorage = req.storageTbNeeded * cloud.storagePricePerTbMonth;
  const cloudEgress = req.monthlyEgressGb * cloud.egressPricePerGb;
  const cloudMonthlyTotal = cloudCompute + cloudStorage + cloudEgress + cloud.managedServicesFeeMonthly;

  // 2. Bare Metal витрати
  const serversByCpu = Math.ceil(req.vCpuNeeded / metal.vCpuPerServer);
  const serversByRam = Math.ceil(req.ramGbNeeded / metal.ramGbPerServer);
  const serversByStorage = Math.ceil(req.storageTbNeeded / metal.storageTbPerServer);
  const serverCount = Math.max(serversByCpu, serversByRam, serversByStorage);

  const totalCapEx = serverCount * metal.serverCapEx;
  const monthlyAmortization = totalCapEx / req.horizonMonths;

  const rackFee = serverCount * metal.rackUnitMonthlyFee;
  const kwhUsedMonthly = serverCount * metal.serverPowerDrawKw * hoursPerMonth * metal.pueRatio;
  const powerFee = kwhUsedMonthly * metal.powerKwPerHourPrice;
  
  const bareMetalMonthlyTotal = monthlyAmortization + rackFee + powerFee + 
                                metal.unmeteredBandwidthMonthlyFee + 
                                metal.opsSalaryAllocationMonthly;

  const monthlySavings = cloudMonthlyTotal - bareMetalMonthlyTotal;
  const paybackPeriodMonths = monthlySavings > 0 ? totalCapEx / monthlySavings : Infinity;

  return {
    cloudMonthlyTotal,
    bareMetalMonthlyTotal,
    bareMetalCapExTotal: totalCapEx,
    monthlySavings,
    paybackPeriodMonths
  };
}
