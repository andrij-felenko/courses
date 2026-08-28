interface MediaKeyStatusMap {
  readonly size: number;
  has(keyId: BufferSource): boolean;
  get(keyId: BufferSource): MediaKeyStatus | undefined;
  entries(): IterableIterator<[ArrayBuffer, MediaKeyStatus]>;
  keys(): IterableIterator<ArrayBuffer>;
  values(): IterableIterator<MediaKeyStatus>;
}

type MediaKeyStatus = 
  | "usable"                            // Ключ активний, розшифрування працює
  | "expired"                           // Термін дії ліцензії вичерпано
  | "released"                          // Ліцензію вивільнено клієнтом
  | "output-restricted"                 // Заборонено політикою виводу (наприклад, потрібен HDCP 2.2)
  | "output-downscaled"                 // Дозволено лише зі штучним зниженням роздільної здатності
  | "status-pending"                    // Статус обробляється CDM
  | "internal-error";                   // Збій у криптографічному модулі
