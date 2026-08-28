// Погано: рядок, з якого в проді нічого не спитаєш.
logger.info("команду надіслано");

// Добре: подія з полями — її можна фільтрувати й агрегувати постфактум.
logger.info({
  event: "device.command",
  tenant: tenantId,
  device: deviceId,
  command: cmd.name,
  outcome,                              // "ok" | "timeout" | "rejected"
  latencyMs: elapsed,
});
