import * as http from "node:http";
import type { AddressInfo } from "node:net";
import type { Deliverable } from "./contract.ts";

/**
 * Реалізація сервісу провайдера (підрядника).
 * Містить бізнес-ендпоїнти та спеціальний тестовий обробник станів (Provider State Handler),
 * який під час верифікації контракту готує дані перед виконанням кожного сценарію.
 */
export class ProviderService {
  private server: http.Server | null = null;
  private listeningPort = 0;

  /** Внутрішня база даних актів робіт у пам'яті */
  private deliverables: Map<string, Deliverable> = new Map();

  constructor() {
    this.resetToInitialState();
  }

  /** Скидання даних до базового початкового стану */
  public resetToInitialState(): void {
    this.deliverables.clear();
  }

  /**
   * Налаштування конкретного стану провайдера за запитом верифікатора.
   */
  public setupState(stateName: string): void {
    switch (stateName) {
      case "акт робіт 101 передано підрядником на рецензування":
      case "акт робіт 101 очікує на підписання":
        this.deliverables.set("101", {
          id: "101",
          title: "Модуль криптографічної автентифікації",
          contractor: "ПП Безпека-Систем",
          status: "SUBMITTED",
          artifactsCount: 5,
        });
        break;

      case "акт робіт 999 відсутній у реєстрі":
        this.deliverables.delete("999");
        break;

      default:
        console.warn(`[Провайдер] Невідомий стан провайдера: "${stateName}". Скидаємо до базового.`);
        break;
    }
  }

  /** Запустити сервер провайдера */
  public async start(port = 0): Promise<number> {
    return new Promise((resolve, reject) => {
      this.server = http.createServer(async (req, res) => {
        try {
          await this.routeRequest(req, res);
        } catch (err) {
          res.statusCode = 500;
          res.setHeader("Content-Type", "application/json");
          res.end(JSON.stringify({ error: "Внутрішня помилка сервера", details: String(err) }));
        }
      });

      this.server.listen(port, "127.0.0.1", () => {
        const addr = this.server?.address() as AddressInfo;
        this.listeningPort = addr.port;
        resolve(this.listeningPort);
      });

      this.server.on("error", reject);
    });
  }

  /** Отримати базовий URL сервісу */
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

  private async routeRequest(req: http.IncomingMessage, res: http.ServerResponse): Promise<void> {
    const method = req.method?.toUpperCase() || "GET";
    const url = req.url || "/";

    // 1. Тестовий ендпоїнт перемикання станів (Provider State Endpoint)
    if (method === "POST" && url === "/_provider_state") {
      const body = await this.readBody(req);
      const parsed = JSON.parse(body || "{}") as { state?: string };
      if (parsed.state) {
        this.setupState(parsed.state);
      }
      res.statusCode = 200;
      res.setHeader("Content-Type", "application/json");
      res.end(JSON.stringify({ status: "ok", currentState: parsed.state }));
      return;
    }

    // 2. GET /deliverables/:id
    const getMatch = /^\/deliverables\/([^/]+)$/.exec(url);
    if (method === "GET" && getMatch) {
      const id = decodeURIComponent(getMatch[1]);
      const deliverable = this.deliverables.get(id);

      if (!deliverable) {
        res.statusCode = 404;
        res.setHeader("Content-Type", "application/json");
        res.end(JSON.stringify({ error: `Акт робіт з номером ${id} не знайдено` }));
        return;
      }

      res.statusCode = 200;
      res.setHeader("Content-Type", "application/json");
      res.end(JSON.stringify(deliverable));
      return;
    }

    // 3. POST /deliverables/:id/accept
    const acceptMatch = /^\/deliverables\/([^/]+)\/accept$/.exec(url);
    if (method === "POST" && acceptMatch) {
      const id = decodeURIComponent(acceptMatch[1]);
      const deliverable = this.deliverables.get(id);

      if (!deliverable) {
        res.statusCode = 404;
        res.setHeader("Content-Type", "application/json");
        res.end(JSON.stringify({ error: `Акт робіт з номером ${id} не знайдено` }));
        return;
      }

      const body = await this.readBody(req);
      const parsedBody = JSON.parse(body || "{}") as { acceptedBy?: string; comment?: string };

      deliverable.status = "ACCEPTED";
      this.deliverables.set(id, deliverable);

      res.statusCode = 200;
      res.setHeader("Content-Type", "application/json");
      res.end(
        JSON.stringify({
          id: deliverable.id,
          status: "ACCEPTED",
          acceptedAt: "2026-09-09T00:00:00.000Z",
        })
      );
      return;
    }

    // 4. Невідомий маршрут
    res.statusCode = 404;
    res.setHeader("Content-Type", "application/json");
    res.end(JSON.stringify({ error: "Маршрут не знайдено" }));
  }

  private readBody(req: http.IncomingMessage): Promise<string> {
    return new Promise((resolve, reject) => {
      const chunks: Buffer[] = [];
      req.on("data", (chunk: Buffer) => chunks.push(chunk));
      req.on("end", () => resolve(Buffer.concat(chunks).toString("utf8")));
      req.on("error", reject);
    });
  }
}
