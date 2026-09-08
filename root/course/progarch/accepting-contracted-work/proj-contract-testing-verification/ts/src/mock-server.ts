import * as http from "node:http";
import type { AddressInfo } from "node:net";
import type { Contract, HttpMethod, Interaction } from "./contract.ts";
import { matchPayload, saveContract } from "./contract.ts";

/**
 * Локальний тестовий мок-сервер споживача (Consumer Mock Server).
 * Фіксує очікувані запити під час виконання клієнтських тестів
 * та генерує узгоджений JSON-контракт взаємодії.
 */
export class ConsumerMockServer {
  private expectedInteractions: Interaction[] = [];
  private matchedInteractions: Set<Interaction> = new Set();
  private server: http.Server | null = null;
  private listeningPort = 0;

  /** Додати очікувану взаємодію перед запуском сценарію */
  public addInteraction(interaction: Interaction): void {
    this.expectedInteractions.push(interaction);
  }

  /** Очистити список очікувань */
  public clearInteractions(): void {
    this.expectedInteractions = [];
    this.matchedInteractions.clear();
  }

  /** Запустити локальний HTTP-сервер на випадковому вільному порту */
  public async start(): Promise<number> {
    return new Promise((resolve, reject) => {
      this.server = http.createServer(async (req, res) => {
        try {
          await this.handleRequest(req, res);
        } catch (err) {
          res.statusCode = 500;
          res.setHeader("Content-Type", "application/json");
          res.end(JSON.stringify({ error: "Внутрішня помилка мок-сервера", details: String(err) }));
        }
      });

      this.server.listen(0, "127.0.0.1", () => {
        const addr = this.server?.address() as AddressInfo;
        this.listeningPort = addr.port;
        resolve(this.listeningPort);
      });

      this.server.on("error", reject);
    });
  }

  /** Отримати базовий URL мок-сервера */
  public getBaseUrl(): string {
    return `http://127.0.0.1:${this.listeningPort}`;
  }

  /** Зупинити сервер */
  public async stop(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.server) {
        resolve();
        return;
      }
      this.server.close((err) => {
        if (err) reject(err);
        else resolve();
      });
    });
  }

  /** Перевірити, що всі зареєстровані взаємодії були викликані, та зберегти контракт */
  public verifyAndEmitContract(
    consumerName: string,
    providerName: string,
    outputPath: string
  ): Contract {
    const missing = this.expectedInteractions.filter((i) => !this.matchedInteractions.has(i));
    if (missing.length > 0) {
      const descs = missing.map((m) => `«${m.description}»`).join(", ");
      throw new Error(`Помилка контрактного тесту: не всі очікування були виконані: ${descs}`);
    }

    const contract: Contract = {
      consumer: { name: consumerName },
      provider: { name: providerName },
      interactions: [...this.expectedInteractions],
      metadata: {
        createdAt: new Date().toISOString(),
        specificationVersion: "1.0.0",
      },
    };

    saveContract(contract, outputPath);
    return contract;
  }

  private async handleRequest(req: http.IncomingMessage, res: http.ServerResponse): Promise<void> {
    const method = (req.method || "GET").toUpperCase() as HttpMethod;
    const url = req.url || "/";
    const bodyStr = await this.readRequestBody(req);
    let parsedBody: unknown = null;
    if (bodyStr) {
      try {
        parsedBody = JSON.parse(bodyStr);
      } catch {
        parsedBody = bodyStr;
      }
    }

    // Шукаємо очікувану взаємодію, що відповідає запиту
    const match = this.expectedInteractions.find((item) => {
      if (item.request.method !== method) return false;
      if (item.request.path !== url) return false;

      if (item.request.body !== undefined) {
        const bodyMatch = matchPayload(item.request.body, parsedBody);
        if (!bodyMatch.matches) return false;
      }
      return true;
    });

    if (!match) {
      res.statusCode = 501;
      res.setHeader("Content-Type", "application/json");
      res.end(
        JSON.stringify({
          error: "Непередбачений контрактний запит (Unexpected Request)",
          received: { method, path: url, body: parsedBody },
          registeredInteractionsCount: this.expectedInteractions.length,
        })
      );
      return;
    }

    this.matchedInteractions.add(match);

    res.statusCode = match.response.status;
    const headers = match.response.headers || { "Content-Type": "application/json" };
    for (const [key, value] of Object.entries(headers)) {
      res.setHeader(key, value);
    }

    if (match.response.body !== undefined) {
      res.end(JSON.stringify(match.response.body));
    } else {
      res.end();
    }
  }

  private readRequestBody(req: http.IncomingMessage): Promise<string> {
    return new Promise((resolve, reject) => {
      const chunks: Buffer[] = [];
      req.on("data", (chunk: Buffer) => chunks.push(chunk));
      req.on("end", () => resolve(Buffer.concat(chunks).toString("utf8")));
      req.on("error", reject);
    });
  }
}
