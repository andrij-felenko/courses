import { AsyncLocalStorage } from 'node:async_hooks';
import * as crypto from 'node:crypto';

export interface TraceContext {
  version: string;
  traceId: string;
  spanId: string;
  flags: string;
}

export const traceStorage = new AsyncLocalStorage<TraceContext>();

export function extractTraceparent(header: string | null): TraceContext | null {
  if (!header || header.length < 55) return null;
  const parts = header.split('-');
  if (parts.length < 4) return null;

  const [version, traceId, spanId, flags] = parts;
  if (version === 'ff' || (version === '00' && header.length !== 55)) return null;
  if (!/^[0-9a-fA-F]{32}$/.test(traceId) || /^0{32}$/.test(traceId)) return null;
  if (!/^[0-9a-fA-F]{16}$/.test(spanId) || /^0{16}$/.test(spanId)) return null;
  if (!/^[0-9a-fA-F]{2}$/.test(flags)) return null;

  return {
    version,
    traceId: traceId.toLowerCase(),
    spanId: spanId.toLowerCase(),
    flags: flags.toLowerCase()
  };
}

export function formatTraceparent(ctx: TraceContext): string {
  return `${ctx.version}-${ctx.traceId}-${ctx.spanId}-${ctx.flags}`;
}

export function generateSpanId(): string {
  return crypto.randomBytes(8).toString('hex');
}

export function generateTraceId(): string {
  return crypto.randomBytes(16).toString('hex');
}

// Обгортка для вихідних HTTP-запитів із впровадженням контексту
export async function tracedFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const currentCtx = traceStorage.getStore();
  const headers = new Headers(options.headers);

  if (currentCtx) {
    const childSpanId = generateSpanId();
    const childContext: TraceContext = { ...currentCtx, spanId: childSpanId };
    headers.set('traceparent', formatTraceparent(childContext));
  }

  return fetch(url, { ...options, headers });
}
