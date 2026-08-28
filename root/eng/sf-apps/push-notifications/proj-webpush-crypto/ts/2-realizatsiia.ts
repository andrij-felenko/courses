import * as crypto from 'node:crypto';

export interface WebPushKeys {
  p256dh: string; // Base64URL рядок (65 байтів uncompressed EC point)
  auth: string;   // Base64URL рядок (16 байтів секрету)
}

export class WebPushEncryptor {
  /**
   * Шифрує довільний рядок або JSON-навантаження за стандартом RFC 8291 (aes128gcm)
   */
  public static encrypt(
    keys: WebPushKeys,
    plaintext: string,
    recordSize: number = 4096
  ): Buffer {
    const clientPublicKey = Buffer.from(keys.p256dh, 'base64url');
    const clientAuthSecret = Buffer.from(keys.auth, 'base64url');

    if (clientPublicKey.length !== 65 || clientPublicKey[0] !== 0x04) {
      throw new Error('Ключ client_p256dh має бути 65 байтів у нестисненому форматі');
    }
    if (clientAuthSecret.length !== 16) {
      throw new Error('Секрет client_auth має містити рівно 16 байтів');
    }

    // 1. Генерація ефемерної пари ключів сервера на кривій NIST P-256
    const serverEcdh = crypto.createECDH('prime256v1');
    serverEcdh.generateKeys();
    const serverPublicKey = serverEcdh.getPublicKey(); // 65 байтів uncompressed

    // 2. Обчислення спільного секрету ECDH
    const sharedEcdhSecret = serverEcdh.computeSecret(clientPublicKey);

    // 3. Виведення IKM через HKDF з автентифікаційним секретом клієнта
    // key_info = "WebPush: info\0" || client_p256dh || server_p256dh
    const keyInfo = Buffer.concat([
      Buffer.from('WebPush: info\0', 'utf8'),
      clientPublicKey,
      serverPublicKey
    ]);

    const ikm = crypto.hkdfSync(
      'sha256',
      sharedEcdhSecret,
      clientAuthSecret,
      keyInfo,
      32
    );

    // 4. Генерація випадкової солі (16 байтів)
    const salt = crypto.randomBytes(16);

    // 5. Виведення сесійного ключа (CEK, 16 B) та вектора Nonce (12 B)
    const cekInfo = Buffer.from('Content-Encoding: aes128gcm\0', 'utf8');
    const nonceInfo = Buffer.from('Content-Encoding: nonce\0', 'utf8');

    const cek = Buffer.from(crypto.hkdfSync('sha256', ikm, salt, cekInfo, 16));
    const nonce = Buffer.from(crypto.hkdfSync('sha256', ikm, salt, nonceInfo, 12));

    // 6. Доповнення відкритого тексту (Padding) маркером 0x02
    const inputBuffer = Buffer.from(plaintext, 'utf8');
    const paddedBuffer = Buffer.concat([inputBuffer, Buffer.from([0x02])]);

    // 7. Шифрування AES-128-GCM
    const cipher = crypto.createCipheriv('aes-128-gcm', cek, nonce);
    const encryptedBody = Buffer.concat([
      cipher.update(paddedBuffer),
      cipher.final()
    ]);
    const authTag = cipher.getAuthTag(); // 16 байтів

    // 8. Збирання структури кадру aes128gcm
    // [salt (16 B)] || [rs (4 B)] || [idlen (1 B)] || [serverPublicKey (65 B)] || [ciphertext] || [authTag (16 B)]
    const rsBuffer = Buffer.alloc(4);
    rsBuffer.writeUInt32BE(recordSize, 0);

    const idLenBuffer = Buffer.from([serverPublicKey.length]);

    return Buffer.concat([
      salt,
      rsBuffer,
      idLenBuffer,
      serverPublicKey,
      encryptedBody,
      authTag
    ]);
  }
}
