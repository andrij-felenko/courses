import { Pool } from 'pg';

export interface IngestionResult {
  statusCode: number;
  message: string;
  enqueued: boolean;
}

export class WebhookDeduplicationService {
  constructor(private readonly dbPool: Pool) {}

  /**
   * Атомарно реєструє подію та визначає, чи потребує вона доменної обробки.
   */
  async processInboundEvent(
    eventId: string,
    provider: string,
    eventType: string,
    payload: Record<string, unknown>
  ): Promise<IngestionResult> {
    const insertQuery = `
      INSERT INTO inbound_webhook_events (event_id, provider, event_type, status, payload)
      VALUES ($1, $2, $3, 'RECEIVED', $4)
      ON CONFLICT (event_id) DO NOTHING
      RETURNING event_id;
    `;

    const client = await this.dbPool.connect();
    try {
      const result = await client.query(insertQuery, [
        eventId,
        provider,
        eventType,
        JSON.stringify(payload),
      ]);

      // Якщо рядок успішно вставлено — це первинна поява події
      if (result.rowCount && result.rowCount > 0) {
        return {
          statusCode: 200,
          message: 'EVENT_ACCEPTED',
          enqueued: true,
        };
      }

      // Якщо рядок не вставлено — подія є дублікатом
      const statusQuery = `
        SELECT status FROM inbound_webhook_events WHERE event_id = $1;
      `;
      const existing = await client.query(statusQuery, [eventId]);
      const currentStatus = existing.rows[0]?.status;

      // Підтверджуємо прийом дубліката без повторної постановки в чергу
      return {
        statusCode: 200,
        message: `DUPLICATE_ACKNOWLEDGED_STATE_${currentStatus}`,
        enqueued: false,
      };
    } finally {
      client.release();
    }
  }
}
