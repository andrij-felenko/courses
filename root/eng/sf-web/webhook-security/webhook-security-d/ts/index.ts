import express, { Request, Response } from "express";
import crypto from "node:crypto";

interface WebhookConfig {
  primarySecret: string;
  secondarySecret?: string;
  toleranceSeconds: number;
}

class WebhookSecurity {
  constructor(private config: WebhookConfig) {}

  /**
   * Повна верифікація підпису вебхука за стандартом HMAC-SHA256 з міткою часу.
   */
  public verify(rawBody: Buffer, signatureHeader: string): boolean {
    if (!signatureHeader || !rawBody) return false;

    // Парсинг заголовка: t=1719580800,v1=5257a869e7ec...
    const elements = signatureHeader.split(",");
    let timestamp = -1;
    const signatures: string[] = [];

    for (const element of elements) {
      const [key, value] = element.trim().split("=");
      if (!key || !value) continue;
      if (key === "t") {
        timestamp = parseInt(value, 10);
      } else if (key === "v1") {
        signatures.push(value);
      }
    }

    if (timestamp === -1 || signatures.length === 0 || isNaN(timestamp)) {
      return false;
    }

    // Перевірка часового вікна (Time-Window)
    const now = Math.floor(Date.now() / 1000);
    if (Math.abs(now - timestamp) > this.config.toleranceSeconds) {
      return false; // Запит або застарів (>300с), або з далекого майбутнього
    }

    // Підписуваний рядок: timestamp || "." || raw_body
    const payloadToSign = Buffer.concat([
      Buffer.from(`${timestamp}.`, "utf8"),
      rawBody,
    ]);

    const activeSecrets = [this.config.primarySecret];
    if (this.config.secondarySecret) {
      activeSecrets.push(this.config.secondarySecret);
    }

    // Перевірка підпису проти активних секретів (Zero-Downtime Rotation)
    for (const secret of activeSecrets) {
      const expectedHex = crypto
        .createHmac("sha256", secret)
        .update(payloadToSign)
        .digest("hex");

      const expectedBuf = Buffer.from(expectedHex, "utf8");

      for (const sig of signatures) {
        const sigBuf = Buffer.from(sig, "utf8");

        // Безпечне порівняння сталого часу (Constant-Time Comparison)
        if (
          sigBuf.length === expectedBuf.length &&
          crypto.timingSafeEqual(sigBuf, expectedBuf)
        ) {
          return true; // Успішна валідація
        }
      }
    }

    return false;
  }
}

const app = express();
const verifier = new WebhookSecurity({
  primarySecret: process.env.WEBHOOK_PRIMARY_SECRET || "whsec_primary_abc123",
  secondarySecret: process.env.WEBHOOK_SECONDARY_SECRET,
  toleranceSeconds: 300,
});

// КРИТИЧНО: зберігаємо сирі байти для верифікації HMAC
app.post(
  "/api/webhooks",
  express.raw({ type: "application/json", limit: "1mb" }),
  async (req: Request, res: Response) => {
    const sigHeader = req.header("Stripe-Signature") || "";
    const rawBody = req.body as Buffer;

    // 1. Криптографічна перевірка підпису, часу та ротації
    const isValid = verifier.verify(rawBody, sigHeader);
    if (!isValid) {
      return res.status(401).json({ error: "Invalid signature or expired timestamp" });
    }

    // 2. Безпечний розбір JSON лише після валідації
    const event = JSON.parse(rawBody.toString("utf8"));

    // 3. Перевірка ідемпотентності / дедуплікація Replay (псевдокод сховища)
    // const isNew = await redis.set(`webhook:seen:${event.id}`, "1", "NX", "EX", 600);
    // if (!isNew) return res.status(200).json({ received: true, duplicate: true });

    // 4. Передача у чергу задач та негайне підтвердження 200 OK
    // await queue.push(event);
    return res.status(200).json({ received: true });
  }
);
