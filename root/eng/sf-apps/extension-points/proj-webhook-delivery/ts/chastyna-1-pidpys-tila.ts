import { createHmac, timingSafeEqual } from "node:crypto";

// Одна звістка, готова до відправлення: сирий рядок тіла + заголовки.
interface SignedDelivery {
  body: string;             // ті САМІ байти, що підуть по дроту
  headers: Record<string, string>;
}

// Підписуємо рядок "мітка_часу.тіло" — мітка всередині підпису,
// тож програти стару звістку пізніше вже не вийде.
function signWebhook(payload: object, secret: string): SignedDelivery {
  const body = JSON.stringify(payload);          // серіалізуємо РАЗ
  const timestamp = Math.floor(Date.now() / 1000);
  const signedString = `${timestamp}.${body}`;   // час . тіло

  const signature = createHmac("sha256", secret)
    .update(signedString)                         // підписуємо саме цей рядок
    .digest("hex");

  return {
    body,                                         // і надсилаємо ЙОГО, не пере-серіалізуємо
    headers: {
      "Content-Type": "application/json",
      "X-Webhook-Timestamp": String(timestamp),
      "X-Webhook-Signature": `v1=${signature}`,   // версіонуємо схему підпису
    },
  };
}

// Бік ОДЕРЖУВАЧА (для симетрії): звіряємо сталим-у-часі порівнянням
// і відкидаємо надто стару мітку — інакше підпис можна вкрасти й програти.
function verifyWebhook(
  body: string, headerTs: string, headerSig: string,
  secret: string, toleranceSec = 300,
): boolean {
  const age = Math.abs(Date.now() / 1000 - Number(headerTs));
  if (age > toleranceSec) return false;           // задавнена звістка — геть

  const expected = createHmac("sha256", secret)
    .update(`${headerTs}.${body}`).digest("hex");
  const got = headerSig.replace(/^v1=/, "");

  const a = Buffer.from(expected), b = Buffer.from(got);
  return a.length === b.length && timingSafeEqual(a, b); // час порівняння НЕ видає підпис
}
