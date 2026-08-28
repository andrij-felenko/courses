// Обробка вебхуків із захистом від порушення порядку
async function handleStripeWebhook(event: StripeEvent) {
  const tenant = await tenantRepo.findById(event.tenantId);
  
  if (event.createdTimestamp <= tenant.lastProcessedBillingEventTime) {
    // Подія застаріла і прийшла поза порядком — мовчки ігноруємо
    logger.warn(`Out-of-order webhook ignored: ${event.id}`);
    return;
  }

  await db.transaction(async (tx) => {
    await ledger.postTransaction(event);
    await tenantRepo.updateLastBillingTime(tenant.id, event.createdTimestamp);
  });
}
