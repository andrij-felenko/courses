import crypto from "node:crypto";

export interface VerifiedWebhookEvent {
  id: string;
  type: string;
  data: {
    object: Record<string, any>;
  };
}

export class WebhookSignatureVerifier {
  constructor(
    private readonly webhookSecret: string,
    private readonly toleranceSeconds: number = 300
  ) {}

  /**
   * Перевіряє справжність вебхука за сталий час та з урахуванням мітки часу.
   */
  verifyAndParse(rawBody: Buffer, signatureHeader: string): VerifiedWebhookEvent {
    const parts = signatureHeader.split(",");
    let timestamp = "";
    let signature = "";

    for (const part of parts) {
      const [key, value] = part.trim().split("=");
      if (key === "t") timestamp = value;
      if (key === "v1") signature = value;
    }

    if (!timestamp || !signature) {
      throw new Error("Невалідний формат заголовка Stripe-Signature");
    }

    // 1. Перевірка часового вікна (Replay Attack Prevention)
    const eventTime = Number.parseInt(timestamp, 10);
    const currentTime = Math.floor(Date.now() / 1000);
    if (Number.isNaN(eventTime) || Math.abs(currentTime - eventTime) > this.toleranceSeconds) {
      throw new Error("Мітка часу вебхука виходить за межі допустимого вікна (replay attack)");
    }

    // 2. Обчислення очікуваного HMAC-SHA256 підпису
    const signedPayload = `${timestamp}.${rawBody.toString("utf8")}`;
    const hmac = crypto.createHmac("sha256", this.webhookSecret);
    hmac.update(signedPayload);
    const expectedSignature = hmac.digest("hex");

    // 3. Порівняння за сталий час для захисту від timing attacks
    const sigBuffer = Buffer.from(signature, "hex");
    const expectedBuffer = Buffer.from(expectedSignature, "hex");

    if (sigBuffer.length !== expectedBuffer.length || !crypto.timingSafeEqual(sigBuffer, expectedBuffer)) {
      throw new Error("Криптографічний підпис вебхука не збігається");
    }

    return JSON.parse(rawBody.toString("utf8")) as VerifiedWebhookEvent;
  }
}
