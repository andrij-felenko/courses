/** Словник подій, спільний із бекендом. Змінюється тільки разом із ним. */

export type CommandStatus =
    | "QUEUED"
    | "DISPATCHED"
    | "ACK_RECEIVED"
    | "ACK_DUPLICATE"
    | "STARTED"
    | "IN_PROGRESS"
    | "COMPLETED"
    | "FAILED"
    | "EXPIRED"
    | "TIMEOUT";

/** Після цих станів транзакція вже нікуди не рухається. */
export const TERMINAL_STATUSES: ReadonlySet<string> = new Set([
    "COMPLETED",
    "FAILED",
    "EXPIRED",
    "TIMEOUT",
]);

export interface CommandSnapshot {
    cmd_id: string;
    device_id: string;
    op: string;
    status: CommandStatus;
    progress_pct: number;
    value_pct: number;
    error_code: number;
}

export type ServerEvent =
    | { event: "STATUS_UPDATE"; command: CommandSnapshot }
    | { event: "SYNC_SNAPSHOT"; commands: CommandSnapshot[] }
    | { event: "ERROR"; reason: string }
    | { event: "PONG" };

export interface CommandDraft {
    device_id: string;
    op: string;
    params: Record<string, unknown>;
    ttl_sec: number;
    idempotency_key: string;
}

function isSnapshot(value: unknown): value is CommandSnapshot {
    if (typeof value !== "object" || value === null) {
        return false;
    }
    const candidate = value as Partial<CommandSnapshot>;
    return (
        typeof candidate.cmd_id === "string" &&
        typeof candidate.device_id === "string" &&
        typeof candidate.status === "string" &&
        typeof candidate.progress_pct === "number"
    );
}

/**
 * Кадр із сокета — чужі дані: віримо лише тому, що справді перевірили.
 * null означає «незрозумілий кадр», і панель його просто пропускає.
 */
export function parseServerEvent(raw: string): ServerEvent | null {
    let parsed: unknown;
    try {
        parsed = JSON.parse(raw);
    } catch {
        return null;
    }
    if (typeof parsed !== "object" || parsed === null) {
        return null;
    }
    const message = parsed as { event?: unknown; command?: unknown; commands?: unknown; reason?: unknown };

    switch (message.event) {
        case "STATUS_UPDATE":
            return isSnapshot(message.command) ? { event: "STATUS_UPDATE", command: message.command } : null;
        case "SYNC_SNAPSHOT":
            if (!Array.isArray(message.commands)) {
                return null;
            }
            return { event: "SYNC_SNAPSHOT", commands: message.commands.filter(isSnapshot) };
        case "ERROR":
            return { event: "ERROR", reason: String(message.reason ?? "без пояснення") };
        case "PONG":
            return { event: "PONG" };
        default:
            return null;
    }
}
