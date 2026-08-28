// TypeScript Implementation: Typed Interfaces, Async/Await Pipeline
interface TraceContext {
  traceId: string;
  parentSpanId: string;
  currentSpanId: string;
  sampled: boolean;
}

interface UnlockCommand {
  userId: string;
  homeId: string;
  lockId: string;
  trace: TraceContext;
}

interface DeviceTwin {
  lockId: string;
  desiredState: string;
  reportedState: string;
  version: number;
}

interface OutboxEvent {
  id: number;
  aggregateId: string;
  eventType: string;
  payloadJson: string;
  traceId: string;
  spanId: string;
}

function parseTraceparent(header: string): TraceContext {
  if (!header.startsWith('00-') || header.length < 55) {
    throw new Error('Invalid W3C traceparent header');
  }
  const parts = header.split('-');
  return {
    traceId: parts[1],
    parentSpanId: parts[2],
    currentSpanId: 'a1b2c3d4e5f67890',
    sampled: parts[3] === '01',
  };
}

class RequestPipeline {
  async processUnlock(traceparentHdr: string, lockId: string, userId: string): Promise<void> {
    const traceCtx = parseTraceparent(traceparentHdr);
    console.log(`[Trace: ${traceCtx.traceId}] Processing unlock for ${lockId} by ${userId}`);

    const twin: DeviceTwin = {
      lockId,
      desiredState: 'UNLOCKED',
      reportedState: 'LOCKED',
      version: 2,
    };

    const outbox: OutboxEvent = {
      id: 1001,
      aggregateId: lockId,
      eventType: 'LockUnlockCommanded',
      payloadJson: JSON.stringify({ lockId, desired: 'UNLOCKED', userId }),
      traceId: traceCtx.traceId,
      spanId: traceCtx.currentSpanId,
    };

    await this.executeTransaction(twin, outbox);
  }

  private async executeTransaction(twin: DeviceTwin, event: OutboxEvent): Promise<void> {
    console.log('[DB TX BEGIN]');
    console.log(`  UPDATE device_twins SET desired_state='${twin.desiredState}' WHERE id='${twin.lockId}'`);
    console.log(`  INSERT INTO outbox_messages (aggregate_id, event_type, trace_id) VALUES ('${event.aggregateId}', '${event.eventType}', '${event.traceId}')`);
    console.log('[DB TX COMMIT] Success');
  }
}
