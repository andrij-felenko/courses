import { Pool, PoolClient } from 'pg';

export interface InboxEvent {
    messageId: string;
    eventType: string;
    payload: Record<string, unknown>;
}

export class TransactionalInboxConsumer {
    private pool: Pool;
    private workerId: string;
    private leaseSeconds: number;

    constructor(pool: Pool, workerId: string, leaseSeconds = 30) {
        this.pool = pool;
        this.workerId = workerId;
        this.leaseSeconds = leaseSeconds;
    }

    /**
     * Атомарна обробка вхідного повідомлення з дедуплікацією
     */
    async consume(
        event: InboxEvent, 
        businessHandler: (client: PoolClient, payload: Record<string, unknown>) => Promise<void>
    ): Promise<'PROCESSED' | 'DUPLICATE' | 'FAILED'> {
        const client = await this.pool.connect();
        try {
            await client.query('BEGIN');

            // 1. Спроба вставити або перевірити ідентифікатор у таблиці inbox
            const insertQuery = `
                INSERT INTO inbox_messages (message_id, event_type, payload, status, locked_until, locked_by)
                VALUES ($1, $2, $3, 'PROCESSING', NOW() + ($4 || ' seconds')::INTERVAL, $5)
                ON CONFLICT (message_id) DO UPDATE
                SET status = 'PROCESSING',
                    locked_until = NOW() + ($4 || ' seconds')::INTERVAL,
                    locked_by = $5
                WHERE inbox_messages.status = 'RECEIVED'
                   OR (inbox_messages.status = 'PROCESSING' AND inbox_messages.locked_until < NOW())
                RETURNING status;
            `;

            const res = await client.query(insertQuery, [
                event.messageId,
                event.eventType,
                JSON.stringify(event.payload),
                this.leaseSeconds,
                this.workerId
            ]);

            if (res.rowCount === 0) {
                // Повідомлення вже оброблено ('PROCESSED') або активне в іншого воркера
                await client.query('ROLLBACK');
                return 'DUPLICATE';
            }

            // 2. Виконання бізнес-логіки в тій самій локальній транзакції
            await businessHandler(client, event.payload);

            // 3. Оновлення статусу повідомлення на PROCESSED
            const completeQuery = `
                UPDATE inbox_messages
                SET status = 'PROCESSED',
                    processed_at = NOW(),
                    locked_until = NULL,
                    locked_by = NULL
                WHERE message_id = $1;
            `;
            await client.query(completeQuery, [event.messageId]);

            // 4. Фіксація транзакції
            await client.query('COMMIT');
            return 'PROCESSED';

        } catch (error: any) {
            await client.query('ROLLBACK');

            // Окремо фіксуємо невдачу та збільшуємо лічильник спроб
            try {
                const failQuery = `
                    UPDATE inbox_messages
                    SET retry_count = retry_count + 1,
                        last_error = $2,
                        status = CASE WHEN retry_count + 1 >= max_retries THEN 'FAILED' ELSE 'RECEIVED' END,
                        locked_until = NULL,
                        locked_by = NULL
                    WHERE message_id = $1;
                `;
                await this.pool.query(failQuery, [event.messageId, error.message || String(error)]);
            } catch (loggingErr) {
                console.error('Не вдалося зберегти статус помилки в inbox:', loggingErr);
            }

            return 'FAILED';
        } finally {
            client.release();
        }
    }
}
