export interface PricingTier {
  upToUnits: bigint; // BigInt(Number.MAX_SAFE_INTEGER) для безлімітного верхнього рівня
  ratePerUnitMicros: bigint;
}

export class RatingEngine {
  public static calculateGraduatedCost(totalUnits: bigint, tiers: PricingTier[]): bigint {
    let totalCost: bigint = 0n;
    let previousBound: bigint = 0n;

    for (const tier of tiers) {
      if (totalUnits <= previousBound) {
        break;
      }

      const tierCapacity = tier.upToUnits - previousBound;
      const unitsInThisTier = totalUnits < tier.upToUnits 
        ? totalUnits - previousBound 
        : tierCapacity;

      totalCost += unitsInThisTier * tier.ratePerUnitMicros;
      previousBound = tier.upToUnits;
    }

    return totalCost;
  }
}
