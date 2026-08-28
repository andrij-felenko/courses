// ============================================================================
// ВАРІАНТ B (Прагматичний): Модульний моноліт на TypeScript
// Пряма обробка в межах одного процесу з транзакційною гарантією
// ============================================================================

interface TelemetryMetric {
  deviceId: string;
  homeId: string;
  energyKwh: number;
  temperatureC: number;
  timestamp: number;
}

interface AggregateResult {
  homeId: string;
  totalEnergyKwh: number;
  avgTemperatureC: number;
  thresholdExceeded: boolean;
}

export class HomeAnalyticsService {
  // Обробка пачки телеметрії в межах однієї транзакції бази даних
  public async processHourlyBatch(
    homeId: string,
    metrics: TelemetryMetric[],
    maxEnergyThreshold: number
  ): Promise<AggregateResult> {
    if (metrics.length === 0) {
      throw new Error("Empty metrics payload");
    }

    let totalEnergy = 0;
    let tempSum = 0;

    for (const m of metrics) {
      totalEnergy += m.energyKwh;
      tempSum += m.temperatureC;
    }

    const avgTemp = tempSum / metrics.length;
    const alertNeeded = totalEnergy > maxEnergyThreshold;

    // Прямий запис у базу даних у межах однієї ACID-транзакції:
    // await db.transaction(async (tx) => {
    //   await tx.query(
    //     "INSERT INTO hourly_aggregates (home_id, total_energy_kwh, avg_temperature_c) VALUES ($1, $2, $3)",
    //     [homeId, totalEnergy, avgTemp]
    //   );
    //   if (alertNeeded) {
    //     await tx.query(
    //       "INSERT INTO outbox_events (aggregate_type, aggregate_id, event_type, payload) VALUES ($1, $2, $3, $4)",
    //       ["HomeAggregate", homeId, "HIGH_ENERGY_ALERT", JSON.stringify({ homeId, totalEnergy })]
    //     );
    //   }
    // });

    return {
      homeId,
      totalEnergyKwh: totalEnergy,
      avgTemperatureC: avgTemp,
      thresholdExceeded: alertNeeded,
    };
  }
}
