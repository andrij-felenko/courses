// Погано: рядок, з якого в проді нічого не спитаєш.
log.Printf("команду надіслано")

// Добре: подія з полями — її можна фільтрувати й агрегувати постфактум.
slog.Info("device.command",
    "tenant",     tenantID,
    "device",     deviceID,
    "command",    cmd.Name,
    "outcome",    outcome,               // "ok" | "timeout" | "rejected"
    "latency_ms", elapsed.Milliseconds(),
)
