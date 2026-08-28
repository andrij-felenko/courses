function runSimulation(): void {
  const quota = new CreditQuotaManager(10_000_000n); // $10.00 депозит
  const ledger = new DoubleEntryLedger();
  const ingest = new EventIngestEngine();
  const buffer = new BatchEventBuffer(100, 50);

  const tenant = "tenant_alpha_42";
  const tiers: PricingTier[] = [
    { upToUnits: 1000n, ratePerUnitMicros: 2000n }, // $0.002
    { upToUnits: BigInt(Number.MAX_SAFE_INTEGER), ratePerUnitMicros: 1000n }, // $0.001
  ];

  // Крок А: Холд $5.00
  const hold = quota.acquireHold(tenant, "hold_req_9981", 5_000_000n);
  if (!hold) {
    throw new Error("Недостатньо коштів на балансі");
  }

  // Крок Б: Буферизація події
  const eventKey = EventIngestEngine.generateKey(tenant, "req_9981", "worker_node_1");
  const event: UsageEvent = {
    eventId: "evt_1001",
    idempotencyKey: eventKey,
    tenantId: tenant,
    metricName: "llm_tokens",
    quantity: 1500n,
    occurredAt: new Date(),
  };
  buffer.push(event);

  // Крок В: Пакетний скид та дедуплікація
  const batch = buffer.extractBatch();
  for (const ev of batch) {
    const status = ingest.ingestEvent(ev);
    if (status !== IngestStatus.Accepted) {
      quota.releaseHold(hold.reservationId);
      return;
    }
  }

  // Крок Г: Тарифікація (1000*2000 + 500*1000 = 2_500_000n = $2.50)
  const actualCost = RatingEngine.calculateGraduatedCost(event.quantity, tiers);

  // Крок Ґ: Завершення холду
  quota.settleHold(hold.reservationId, actualCost);

  // Крок Д: Подвійний запис у реєстр
  ledger.recordUsageCharge("tx_88112", tenant, actualCost, event.eventId);

  console.log(`Баланс клієнта: $${Number(quota.getAvailableBalance()) / 1_000_000}`);
  console.log(`Аудит реєстру валідний: ${ledger.verifyAuditInvariant()}`);
}

runSimulation();
