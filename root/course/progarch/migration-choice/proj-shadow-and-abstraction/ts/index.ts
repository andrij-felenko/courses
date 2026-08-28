import http from 'http';
import fetch from 'node-fetch';

export class ShadowProxy {
  constructor(
    private legacyUrl: string,
    private shadowUrl: string
  ) {}

  public async handleRequest(req: http.IncomingMessage, res: http.ServerResponse): Promise<void> {
    const chunks: Buffer[] = [];
    for await (const chunk of req) {
      chunks.push(chunk);
    }
    const bodyBuffer = Buffer.concat(chunks);

    // 1. Синхронний виклик на Legacy
    const legacyStart = Date.now();
    const legacyResponse = await fetch(`${this.legacyUrl}${req.url}`, {
      method: req.method,
      headers: req.headers as Record<string, string>,
      body: req.method !== 'GET' ? bodyBuffer : undefined,
    });
    const legacyLatency = Date.now() - legacyStart;
    const legacyBody = await legacyResponse.buffer();

    // 2. Асинхронне тіньове дублювання (Fire-and-forget)
    setImmediate(async () => {
      try {
        const shadowStart = Date.now();
        const shadowResponse = await fetch(`${this.shadowUrl}${req.url}`, {
          method: req.method,
          headers: { ...req.headers, 'x-dark-launch-shadow': 'true' } as Record<string, string>,
          body: req.method !== 'GET' ? bodyBuffer : undefined,
        });
        const shadowLatency = Date.now() - shadowStart;
        const shadowBody = await shadowResponse.buffer();

        this.validateDiff(legacyBody, shadowBody, legacyLatency, shadowLatency, req.url || '');
      } catch (err) {
        console.warn('[ShadowProxy] Shadow call failed:', err);
      }
    });

    // 3. Повертаємо відповідь legacy-системи клієнту
    res.writeHead(legacyResponse.status, Object.fromEntries(legacyResponse.headers.entries()));
    res.end(legacyBody);
  }

  private validateDiff(legBody: Buffer, shdBody: Buffer, legLat: number, shdLat: number, url: string): void {
    try {
      const legJson = JSON.parse(legBody.toString('utf-8'));
      const shdJson = JSON.parse(shdBody.toString('utf-8'));
      delete legJson.timestamp;
      delete shdJson.timestamp;

      if (JSON.stringify(legJson) !== JSON.stringify(shdJson)) {
        console.error(`[ShadowDiffMismatch] URL: ${url} | Legacy: ${legLat}ms | Shadow: ${shdLat}ms`);
      }
    } catch {
      if (!legBody.equals(shdBody)) {
        console.error(`[ShadowRawMismatch] URL: ${url}`);
      }
    }
  }
}
