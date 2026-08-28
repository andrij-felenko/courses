type CommandStatus = "IDLE" | "PENDING" | "ACK_RECEIVED" | "EXECUTING" | "CONFIRMED" | "ERROR";

class ValveControlWidget {
    private ws: WebSocket;
    private state: CommandStatus = "IDLE";
    private activeCmdId: string | null = null;
    private timeoutTimer: number | null = null;

    constructor(wsUrl: string) {
        this.ws = new WebSocket(wsUrl);
        this.ws.onmessage = (event) => this.handleMessage(JSON.parse(event.data));
    }

    public sendPositionCommand(deviceId: string, targetPct: number) {
        if (this.state === "PENDING" || this.state === "EXECUTING") {
            console.warn("Операція вже виконується на залізі. Зачекайте завершення.");
            return;
        }

        this.state = "PENDING";
        this.updateUI("Відправка наказу...", 0);

        // Таймер захисного відкату при втраті зв'язку (12 секунд)
        this.timeoutTimer = window.setTimeout(() => {
            if (this.state !== "CONFIRMED") {
                this.state = "ERROR";
                this.updateUI("Помилка: таймаут зв'язку із залізом", 0);
            }
        }, 12000);

        this.ws.send(JSON.stringify({
            action: "SEND_COMMAND",
            device_id: deviceId,
            op: "set_valve_position",
            params: { target_pct: targetPct },
            ttl_sec: 60
        }));
    }

    private handleMessage(msg: any) {
        if (msg.event === "COMMAND_ENQUEUED") {
            this.activeCmdId = msg.cmd_id;
            this.state = "PENDING";
            this.updateUI("Прийнято сервером...", 5);
        } else if (msg.event === "STATUS_UPDATE" && msg.cmd_id === this.activeCmdId) {
            switch (msg.status) {
                case "ACK_RECEIVED":
                    this.state = "PENDING";
                    this.updateUI("Вузол отримав команду (ACK)", 15);
                    break;
                case "STARTED":
                case "IN_PROGRESS":
                    this.state = "EXECUTING";
                    this.updateUI(`Виконання приводом: ${msg.progress_pct}%`, msg.progress_pct);
                    break;
                case "COMPLETED":
                    this.state = "CONFIRMED";
                    if (this.timeoutTimer) clearTimeout(this.timeoutTimer);
                    this.updateUI(`Успішно завершено! Положення: ${msg.current_value}%`, 100);
                    setTimeout(() => { this.state = "IDLE"; }, 2500);
                    break;
                case "FAILED":
                case "EXPIRED":
                    this.state = "ERROR";
                    if (this.timeoutTimer) clearTimeout(this.timeoutTimer);
                    this.updateUI(`Відмова заліза: код ${msg.error_code || 'невідомо'}`, 0);
                    break;
            }
        }
    }

    private updateUI(statusText: string, progressPct: number) {
        console.log(`[UI UPDATE] Стан: ${this.state} | ${statusText} | Прогрес: ${progressPct}%`);
    }
}
