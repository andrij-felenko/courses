import { ControlLink } from "./link.js";
import { CommandSnapshot, ServerEvent, TERMINAL_STATUSES } from "./protocol.js";

/** Скільки чекаємо на звіт заліза, перш ніж вважати лінк утраченим. */
const LINK_TIMEOUT_MS = 12_000;

const BUSY_STATUSES: ReadonlySet<string> = new Set([
    "QUEUED",
    "DISPATCHED",
    "ACK_RECEIVED",
    "ACK_DUPLICATE",
    "STARTED",
    "IN_PROGRESS",
]);

function must<T extends Element>(root: ParentNode, selector: string): T {
    const element = root.querySelector<T>(selector);
    if (element === null) {
        throw new Error(`віджет неповний: немає ${selector}`);
    }
    return element;
}

/**
 * Віджет засувки: автомат станів, що живе між кліком оператора і звітом заліза.
 * Головне тут — жодного оптимізму: повзунок стає в нове положення лише тоді,
 * коли про це сказало залізо.
 */
export class ValveWidget {
    private readonly button: HTMLButtonElement;
    private readonly slider: HTMLInputElement;
    private readonly bar: HTMLElement;
    private readonly label: HTMLElement;

    private status = "IDLE";
    private activeCmdId: string | null = null;
    private confirmedPct = 0;
    private progressPct = 0;
    private message = "Готово до роботи";
    private online = false;
    private timeoutTimer: number | null = null;

    constructor(
        private readonly root: HTMLElement,
        private readonly link: ControlLink,
        private readonly deviceId: string,
    ) {
        this.button = must<HTMLButtonElement>(root, '[data-role="send"]');
        this.slider = must<HTMLInputElement>(root, '[data-role="target"]');
        this.bar = must<HTMLElement>(root, '[data-role="bar"]');
        this.label = must<HTMLElement>(root, '[data-role="status"]');

        this.confirmedPct = Number(this.slider.value) || 0;
        this.button.addEventListener("click", () => {
            void this.send();
        });
        this.render();
    }

    setOnline(online: boolean): void {
        this.online = online;
        if (!online) {
            this.message = "Зв'язок із сервером утрачено, відновлюємо…";
        } else if (this.activeCmdId === null) {
            this.message = "Готово до роботи";
        }
        this.render();
    }

    async send(): Promise<void> {
        if (this.busy) {
            return;              // кнопка вже заблокована, але клік міг прийти з клавіатури
        }
        if (!this.online) {
            this.message = "Немає зв'язку із сервером";
            this.render();
            return;
        }
        const target = Number(this.slider.value);
        if (!Number.isFinite(target) || target < 0 || target > 100) {
            this.message = "Положення має бути від 0 до 100 %";
            this.render();
            return;
        }

        this.status = "QUEUED";
        this.progressPct = 0;
        this.message = "Відправляємо наказ…";
        this.armTimeout();
        this.render();

        try {
            this.activeCmdId = await this.link.postCommand({
                device_id: this.deviceId,
                op: "set_valve_position",
                params: { target_pct: target },
                ttl_sec: 60,
                idempotency_key: crypto.randomUUID(),
            });
            this.message = "Сервер поставив наказ у чергу";
            this.render();
        } catch (error) {
            const reason = error instanceof Error ? error.message : String(error);
            this.fail(`Сервер відмовив: ${reason}`);
        }
    }

    applyEvent(event: ServerEvent): void {
        switch (event.event) {
            case "SYNC_SNAPSHOT":
                this.adopt(event.commands);
                return;
            case "ERROR":
                this.message = `Сервер: ${event.reason}`;
                this.render();
                return;
            case "PONG":
                return;
            case "STATUS_UPDATE":
                break;
        }

        const command = event.command;
        if (command.device_id !== this.deviceId) {
            return;
        }
        if (this.activeCmdId === null && !TERMINAL_STATUSES.has(command.status)) {
            // Транзакцію почала інша панель або ми самі до розриву: підхоплюємо.
            this.activeCmdId = command.cmd_id;
            this.armTimeout();
        }
        if (command.cmd_id !== this.activeCmdId) {
            return;
        }
        this.consume(command);
    }

    private adopt(commands: CommandSnapshot[]): void {
        const mine = commands.find(
            (command) => command.device_id === this.deviceId && !TERMINAL_STATUSES.has(command.status),
        );
        if (mine === undefined) {
            if (this.activeCmdId !== null) {
                // Поки нас не було, все закінчилося — і ми не знаємо чим.
                this.fail("Стан транзакції втрачено, перевірте залізо");
            }
            return;
        }
        this.activeCmdId = mine.cmd_id;
        this.armTimeout();
        this.consume(mine);
    }

    private consume(command: CommandSnapshot): void {
        this.status = command.status;
        switch (command.status) {
            case "QUEUED":
            case "DISPATCHED":
                this.message = "Наказ у черзі пристрою";
                break;
            case "ACK_RECEIVED":
                this.message = "Плата прийняла команду";
                this.progressPct = Math.max(this.progressPct, 5);
                break;
            case "ACK_DUPLICATE":
                this.message = "Плата вже виконує цей наказ";
                break;
            case "STARTED":
            case "IN_PROGRESS":
                this.progressPct = command.progress_pct;
                this.message = `Привід у русі: ${command.progress_pct} %`;
                break;
            case "COMPLETED":
                this.confirmedPct = command.value_pct;
                this.slider.value = String(this.confirmedPct);
                this.progressPct = 100;
                this.message = `Готово, положення ${this.confirmedPct} %`;
                break;
            case "FAILED":
            case "EXPIRED":
            case "TIMEOUT":
                this.fail(`Відмова заліза (код ${command.error_code})`);
                return;
        }

        if (TERMINAL_STATUSES.has(command.status)) {
            this.activeCmdId = null;
            this.disarmTimeout();
        }
        this.render();
    }

    private armTimeout(): void {
        this.disarmTimeout();
        this.timeoutTimer = window.setTimeout(() => {
            this.timeoutTimer = null;
            this.fail("Таймаут лінка: залізо не відзвітувало");
        }, LINK_TIMEOUT_MS);
    }

    private disarmTimeout(): void {
        if (this.timeoutTimer !== null) {
            window.clearTimeout(this.timeoutTimer);
            this.timeoutTimer = null;
        }
    }

    /** Захисний відкат: повзунок повертається до останнього підтвердженого стану. */
    private fail(message: string): void {
        this.disarmTimeout();
        this.status = "ERROR";
        this.activeCmdId = null;
        this.progressPct = 0;
        this.message = message;
        this.slider.value = String(this.confirmedPct);
        this.render();
    }

    private get busy(): boolean {
        return this.activeCmdId !== null || BUSY_STATUSES.has(this.status);
    }

    private render(): void {
        this.root.dataset.state = this.status;
        this.bar.style.width = `${Math.max(0, Math.min(100, this.progressPct))}%`;
        this.label.textContent = this.message;
        this.button.disabled = this.busy || !this.online;
    }
}
