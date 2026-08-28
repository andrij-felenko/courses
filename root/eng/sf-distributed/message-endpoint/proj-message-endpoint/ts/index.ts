// TypeScript / Node.js асинхронний Message Endpoint

interface MessageHeaders {
    id: string;
    partitionKey: string;
    destination: string;
    timestampMs: number;
}

interface PaymentEvent {
    orderId: string;
    accountId: string;
    amountCents: number;
    action: "CREATE" | "DEPOSIT" | "WITHDRAW";
}

interface Message<T> {
    headers: MessageHeaders;
    payload: T;
}

type AckCallback = (id: string, status: "ACK" | "NACK" | "DLQ", reason?: string) => void;

class TsInbox {
    private processed = new Set<string>();

    tryClaim(id: string): boolean {
        if (this.processed.has(id)) return false;
        this.processed.add(id);
        return true;
    }
}

class TsKeyPartitionedEndpoint {
    private queues: Array<Array<{ msg: Message<PaymentEvent>; cb: AckCallback }>>;
    private busy: boolean[];
    private inbox = new TsInbox();

    constructor(private workerCount: number = 3) {
        this.queues = Array.from({ length: workerCount }, () => []);
        this.busy = Array.from({ length: workerCount }, () => false);
    }

    private hash(key: string): number {
        let h = 0;
        for (let i = 0; i < key.length; i++) {
            h = (Math.imul(31, h) + key.charCodeAt(i)) | 0;
        }
        return Math.abs(h) % this.workerCount;
    }

    dispatch(msg: Message<PaymentEvent>, cb: AckCallback): void {
        const workerId = this.hash(msg.headers.partitionKey);
        this.queues[workerId].push({ msg, cb });
        this.scheduleWorker(workerId);
    }

    private async scheduleWorker(workerId: number): Promise<void> {
        if (this.busy[workerId]) return;
        this.busy[workerId] = true;

        while (this.queues[workerId].length > 0) {
            const task = this.queues[workerId].shift()!;
            
            // 1. Дедуплікація через Inbox
            if (!this.inbox.tryClaim(task.msg.headers.id)) {
                console.log(`  [TS-Worker ${workerId}] ДУБЛІКАТ ${task.msg.headers.id} -> ACK`);
                task.cb(task.msg.headers.id, "ACK");
                continue;
            }

            // 2. Бізнес-обробка
            try {
                if (task.msg.payload.amountCents === 0 && task.msg.payload.action !== "CREATE") {
                    throw new Error("Invalid payment amount: 0");
                }
                console.log(`  [TS-Worker ${workerId}] Успішно: ${task.msg.payload.action} ${task.msg.payload.accountId}`);
                task.cb(task.msg.headers.id, "ACK");
            } catch (err: any) {
                console.log(`  [TS-Worker ${workerId}] ОТРУЙНИЙ ПАКЕТ ${task.msg.headers.id} -> DLQ`);
                task.cb(task.msg.headers.id, "DLQ", err.message);
            }
        }

        this.busy[workerId] = false;
    }
}
