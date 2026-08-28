// Повний цикл підписування та перевірки у TypeScript
async function runWebCryptoHmacDemo(): Promise<void> {
    const rawKey = new Uint8Array([0x0b, 0x0b, 0x0b, 0x0b, 0x0b, 0x0b, 0x0b, 0x0b,
                                  0x0b, 0x0b, 0x0b, 0x0b, 0x0b, 0x0b, 0x0b, 0x0b,
                                  0x0b, 0x0b, 0x0b, 0x0b]);
    const message = new TextEncoder().encode("Hi There");

    // 1. Імпорт ключа в захищений криптографічний контекст
    const cryptoKey: CryptoKey = await crypto.subtle.importKey(
        "raw",
        rawKey,
        { name: "HMAC", hash: { name: "SHA-256" } },
        false, // Заборона експорту значення ключа в JS-пам'ять
        ["sign", "verify"]
    );

    // 2. Обчислення підпису
    const signatureBuffer: ArrayBuffer = await crypto.subtle.sign(
        "HMAC",
        cryptoKey,
        message
    );

    // 3. Константна перевірка автентичності
    const isValid: boolean = await crypto.subtle.verify(
        "HMAC",
        cryptoKey,
        signatureBuffer,
        message
    );

    console.log(`Статус перевірки: ${isValid ? "OK" : "FAILED"}`);
}
