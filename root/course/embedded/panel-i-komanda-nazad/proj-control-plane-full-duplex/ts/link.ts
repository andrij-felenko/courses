import { CommandDraft, ServerEvent, parseServerEvent } from "./protocol.js";

const BACKOFF_BASE_MS = 500;
const BACKOFF_CAP_MS = 15_000;

/**
 * Канал у диспетчер: команди йдуть по HTTP, стани приходять сокетом.
 * Сокет рветься завжди — питання лише коли, тому перепідключення тут
 * не «на майбутнє», а частина роботи.
 */
export class ControlLink {
    private socket: WebSocket | null = null;
    private attempt = 0;
    private stopped = false;
    private retryTimer: number | null = null;

    constructor(
        private readonly apiBase: string,
        private readonly token: string,
        private readonly onEvent: (event: ServerEvent) => void,
        private readonly onLinkState: (online: boolean) => void,
    ) {}

    connect(): void {
        if (this.stopped || this.socket !== null) {
            return;
        }
        const url = new URL("/ws/control", this.apiBase);
        url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
        url.searchParams.set("token", this.token);

        const socket = new WebSocket(url.toString());
        this.socket = socket;

        socket.onopen = () => {
            this.attempt = 0;
            this.onLinkState(true);
            // Поки нас не було, залізо могло і почати, і завершити маневр.
            socket.send(JSON.stringify({ action: "SYNC_PENDING" }));
        };

        socket.onmessage = (message: MessageEvent<string>) => {
            const event = parseServerEvent(String(message.data));
            if (event === null) {
                console.warn("незрозумілий кадр із сокета", message.data);
                return;
            }
            this.onEvent(event);
        };

        socket.onclose = (event: CloseEvent) => {
            this.socket = null;
            this.onLinkState(false);
            if (!this.stopped) {
                this.scheduleReconnect(event.code);
            }
        };
    }

    close(): void {
        this.stopped = true;
        if (this.retryTimer !== null) {
            window.clearTimeout(this.retryTimer);
            this.retryTimer = null;
        }
        this.socket?.close(1000, "сторінка закривається");
    }

    /** Повертає cmd_id, за яким віджет упізнає свої події. */
    async postCommand(draft: CommandDraft): Promise<string> {
        const response = await fetch(new URL("/command", this.apiBase), {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${this.token}`,
            },
            body: JSON.stringify(draft),
        });
        if (!response.ok) {
            const detail = await response.text();
            throw new Error(`${response.status} ${detail.slice(0, 200)}`);
        }
        const body = (await response.json()) as { cmd_id?: unknown };
        if (typeof body.cmd_id !== "string") {
            throw new Error("сервер не повернув cmd_id");
        }
        return body.cmd_id;
    }

    private scheduleReconnect(code: number): void {
        if (code === 4401 || code === 4403) {
            // Токен протух або ролі бракує: довбати сервер немає сенсу.
            console.error("сервер відмовив у доступі до контуру");
            return;
        }
        // Експоненційний відступ із розкидом: інакше сотня панелей після
        // падіння сервера повернеться в одну й ту саму мілісекунду.
        const backoff = Math.min(BACKOFF_BASE_MS * 2 ** this.attempt, BACKOFF_CAP_MS);
        const jitter = Math.floor(Math.random() * 250);
        this.attempt += 1;
        this.retryTimer = window.setTimeout(() => {
            this.retryTimer = null;
            this.connect();
        }, backoff + jitter);
    }
}
