# ⚙️ Обмін ліцензіями: клієнтський EME-конвеєр та серверний обробник ключів

<preknowlist>
- [Спільне шифрування медіа (CENC)](root:sf-security/common-encryption) — заголовок `tenc`, ідентифікатори ключів `KID` та схеми шифрування `cenc` і `cbcs`.
- [Програмний інтерфейс EME та двійковий формат PSSH](root:sf-security/drm-key-delivery/api-eme-interfaces.md) — інтерфейси `MediaKeys`, `MediaKeySession`, структура боксу `pssh`.
- [DRM: як ключ контенту потрапляє в пристрій](root:sf-security/drm-key-delivery) — загальна архітектура захищеної доставки ключів.
</preknowlist>

Цей проект демонструє наскрізну реалізацію двох ключових компонентів системи захищеної доставки ключів: універсального клієнтського EME-контролера мовою TypeScript та високопродуктивного серверного парсера боксів PSSH з механізмом загортання ключів (Key Wrapping) мовами C, C++ та Python. Без практичного розуміння цього коду важко налагодити взаємодію між браузером, проксі-сервером авторизації та криптографічним анклавом.

---

## 1. Архітектура та логіка клієнтського EME-конвеєра

Клієнтський модуль відіграє роль посередника між браузерним рушієм демультиплексування медіаконтейнерів та ізольованим модулем дешифрування контенту (Content Decryption Module, CDM). Оскільки стандарти консорціуму W3C забороняють прикладному коду JavaScript мати прямий доступ до відкритих ключів або виконувати дешифрування кадрів у пам'яті вкладки, увесь обмін побудований навколо асинхронного транспорту непрозорих бінарних повідомлень.

Процес ініціалізації та обслуговування захищеного відтворення складається з кількох взаємопов'язаних етапів.

### 1.1. Перехоплення події виявлення шифрування (`encrypted`)

Коли браузер завантажує перший сегмент ініціалізації (Init Segment або бокс `moov`) у відеобуфер `SourceBuffer`, внутрішній парсер ISO BMFF натрапляє на заголовок захисту `sinf` та бокс `pssh`. У цей момент медіарушій формує подію `encrypted` (типу `MediaEncryptedEvent`).

Подія передає у вебзастосунок два параметри:
- `initDataType`: рядок, що вказує на схему пакування контейнера (у випадку MP4 це `"cenc"`).
- `initData`: масив байтів (`ArrayBuffer`), що містить один або кілька сирих боксів `pssh`.

Головна пастка на цьому етапі полягає в конкурентності: якщо аудіо- та відеопотоки завантажуються з окремих файлів (як це прийнято в адаптивному стримінгу DASH та HLS), подія `encrypted` виникає щонайменше двічі за лічені мілісекунди. Якщо код наївно створюватиме нову сесію на кожну подію, виникне стан перегонів (Race Condition), що призведе до блокування апаратного контексту CDM або повторного завантаження тих самих ліцензій.

Щоб уникнути цього, промислові плеєри застосовують дедуплікацію та чергу ініціалізації:
1. Контролер хешує отриманий `initData` або витягує з нього список `KID`.
2. Якщо для цих ключів уже існує активна сесія у стані обробки або готовності, повторна подія `encrypted` негайно відкидається.
3. Якщо надійшов новий `initData` з іншим набором `KID`, запит ставиться в чергу і виконується лише після завершення попереднього циклу оновлення сесії.

### 1.2. Узгодження можливостей платформи (`requestMediaKeySystemAccess`)

Перед створенням сесії клієнт повинен дізнатися, які рівні захисту підтримуються поточною операційною системою та графічною підсистемою. Для цього викликається `navigator.requestMediaKeySystemAccess()`. 

Плеєр передає список підтримуваних конфігурацій, де вказує:
- Типи кодеків та MIME-типи (наприклад, H.264/AVC або H.265/HEVC).
- Вимоги до апаратного захисту (`robustness`): якщо для 4K-відео вимагається `HW_SECURE_ALL` (Widevine L1 / PlayReady SL3000), а пристрій підтримує лише програмний рівень `SW_SECURE_CRYPTO` (Widevine L3), браузер відхилить запит для цієї конфігурації.

### 1.3. Встановлення сертифіката сервера (`setServerCertificate`)

Для захисту від атак типу «людина посередині» (Man-in-the-Middle) та запобігання витоку унікальних ідентифікаторів пристрою деякі DRM-системи вимагають передачі публічного сертифіката сервера ліцензій. Отримавши цей сертифікат, CDM зашифровує клієнтський челендж ще до того, як віддати його в JavaScript.

### 1.4. Обмін челендж-відповідь та оновлення сесії

Метод `session.generateRequest(initDataType, initData)` передає бінарний PSSH-бокс усередину CDM. Модуль розбирає заголовок, формує цифровий підпис пристрою на базі закритого апаратного ключа і генерує `MediaKeyMessageEvent` (`message`).

JavaScript-код перехоплює бінарний челендж (`event.message`), пакує його в тіло HTTPS POST-запиту, додає заголовок `Authorization: Bearer <JWT>` і надсилає на License Proxy.

Після отримання відповіді від сервера викликається `session.update(licenseData)`. Якщо сертифікат валідний, а ліцензія відповідає правилам, CDM переводить ключі в стан `"usable"` і починає безперервне дешифрування кадрів у захищеному відеотракті.

Нижче наведено повну реалізацію клієнтського координатора `DrmLicenseManager` мовою TypeScript.

```typescript
/**
 * DrmLicenseManager: Універсальний контролер W3C EME для браузерного медіаплеєра.
 */
export interface DrmConfiguration {
  keySystem: string;            // наприклад, 'com.widevine.alpha' або 'com.microsoft.playready'
  licenseServerUrl: string;     // URL проксі-сервера видачі ліцензій
  authToken: string;            // JWT або сесійний токен користувача
  serverCertificate?: Uint8Array; // Публічний сертифікат сервера ліцензій
}

export class DrmLicenseManager {
  private videoElement: HTMLVideoElement;
  private config: DrmConfiguration;
  private mediaKeys: MediaKeys | null = null;
  private activeSession: MediaKeySession | null = null;
  private isInitializing: boolean = false;

  constructor(video: HTMLVideoElement, config: DrmConfiguration) {
    this.videoElement = video;
    this.config = config;
    this.attachEventListeners();
  }

  private attachEventListeners(): void {
    this.videoElement.addEventListener('encrypted', (event: MediaEncryptedEvent) => {
      this.handleEncryptedEvent(event).catch((err) => {
        console.error('[DRM] Критична помилка обробки події encrypted:', err);
      });
    });
  }

  private async handleEncryptedEvent(event: MediaEncryptedEvent): Promise<void> {
    if (!event.initData) {
      console.warn('[DRM] Подія encrypted не містить initData');
      return;
    }

    if (this.isInitializing || this.activeSession) {
      // Сесія вже створена або ініціалізується
      return;
    }

    this.isInitializing = true;

    try {
      if (!this.mediaKeys) {
        await this.setupMediaKeys();
      }

      // Створення тимчасової сесії дешифрування
      const session = this.mediaKeys!.createSession('temporary');
      this.activeSession = session;

      // Підписка на повідомлення від CDM
      session.addEventListener('message', (msgEvent: MediaKeyMessageEvent) => {
        this.handleSessionMessage(session, msgEvent).catch((err) => {
          console.error('[DRM] Помилка доставки ліцензійного челенджу:', err);
        });
      });

      // Підписка на зміну статусу ключів
      session.addEventListener('keystatuseschange', () => {
        this.handleKeyStatusesChange(session);
      });

      const initDataType = event.initDataType || 'cenc';
      console.log(`[DRM] Генерація License Request для initDataType: ${initDataType}`);
      
      // Передаємо PSSH-бокс у CDM для створення Challenge
      await session.generateRequest(initDataType, event.initData);
    } finally {
      this.isInitializing = false;
    }
  }

  private async setupMediaKeys(): Promise<void> {
    const keySystemConfigs: MediaKeySystemConfiguration[] = [
      {
        initDataTypes: ['cenc'],
        audioCapabilities: [
          {
            contentType: 'audio/mp4; codecs="mp4a.40.2"',
            robustness: 'SW_SECURE_CRYPTO'
          }
        ],
        videoCapabilities: [
          {
            contentType: 'video/mp4; codecs="avc1.640028"',
            robustness: 'SW_SECURE_CRYPTO'
          },
          {
            contentType: 'video/mp4; codecs="hvc1.1.6.L153.B0"',
            robustness: 'HW_SECURE_ALL'
          }
        ],
        distinctiveIdentifier: 'optional',
        persistentState: 'optional',
        sessionTypes: ['temporary']
      }
    ];

    console.log(`[DRM] Запит доступу до системи: ${this.config.keySystem}`);
    const keySystemAccess = await navigator.requestMediaKeySystemAccess(
      this.config.keySystem,
      keySystemConfigs
    );

    const mediaKeys = await keySystemAccess.createMediaKeys();

    // Якщо надано сертифікат сервера, завантажуємо його перед запитом ліцензії
    if (this.config.serverCertificate) {
      console.log('[DRM] Встановлення публічного сертифіката сервера ліцензій...');
      await mediaKeys.setServerCertificate(this.config.serverCertificate as unknown as BufferSource);
    }

    // Прив'язка криптографічного контексту до HTML5 Video Element
    await this.videoElement.setMediaKeys(mediaKeys);
    this.mediaKeys = mediaKeys;
    console.log('[DRM] MediaKeys успішно прив\'язано до медіаелемента');
  }

  private async handleSessionMessage(
    session: MediaKeySession,
    event: MediaKeyMessageEvent
  ): Promise<void> {
    const challenge = event.message;
    console.log(`[DRM] Отримано ${challenge.byteLength} байтів челенджу (${event.messageType}). Відправка на сервер...`);

    // Мережевий запит на License Proxy з авторизаційним заголовком
    const response = await fetch(this.config.licenseServerUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/octet-stream',
        'Authorization': `Bearer ${this.config.authToken}`,
        'X-DRM-Message-Type': event.messageType
      },
      body: challenge
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: Сервер ліцензій відхилив запит (${response.statusText})`);
    }

    const licenseData = await response.arrayBuffer();
    console.log(`[DRM] Отримано ліцензійну відповідь: ${licenseData.byteLength} байтів. Оновлення сесії CDM...`);

    // Завантаження зашифрованої ліцензії в CDM
    await session.update(licenseData);
    console.log('[DRM] Сесію CDM успішно оновлено (License Response застосовано)');
  }

  private handleKeyStatusesChange(session: MediaKeySession): void {
    console.log(`[DRM] Зміна статусу ключів (всього ключів у сесії: ${session.keyStatuses.size}):`);
    
    session.keyStatuses.forEach((status: MediaKeyStatus, keyIdBuffer: ArrayBuffer) => {
      const kidHex = Array.from(new Uint8Array(keyIdBuffer))
        .map(b => b.toString(16).padStart(2, '0'))
        .join('');
      
      console.log(`  - KID [${kidHex}]: статус = ${status}`);

      if (status === 'output-restricted') {
        console.warn(`[DRM] Попередження: Ключ ${kidHex} обмежено політикою HDCP. Відео може бути заблоковано.`);
      } else if (status === 'internal-error') {
        console.error(`[DRM] Апаратна помилка TEE під час розгортання ключа ${kidHex}`);
      }
    });
  }

  public async destroy(): Promise<void> {
    if (this.activeSession) {
      await this.activeSession.close();
      this.activeSession = null;
    }
    if (this.videoElement) {
      await this.videoElement.setMediaKeys(null);
    }
    this.mediaKeys = null;
  }
}
```

---

## 2. Двійковий розбір боксу PSSH на сервері

На стороні контентного сервера або пакувальника мультимедійних потоків (Packager) часто виникає потреба проінспектувати або розібрати контейнерний бокс `pssh`, витягнути з нього 16-байтові ідентифікатори `KID` та визначити цільову систему за її 128-бітним `SystemID`.

### Особливості двійкового аналізу

1. **Мережевий порядок байтів (Big-Endian)**: Усі числові поля боксів ISO BMFF (`size`, `flags`, `kid_count`, `data_size`) зберігаються у форматі від старшого до молодшого байта. Парсер повинен виконувати явне перетворення за допомогою функції `read_be32` або стандартних викликів `ntohl`.
2. **Перевірка меж буфера (Bounds Checking)**: Оскільки бокс може бути пошкодженим або сфабрикованим зловмисником для переповнення буфера (Buffer Overflow), кожне зміщення (`offset`) та довжина підблоку перевіряються перед зчитуванням.
3. **Обробка версій 0 та 1**: У версії 0 лічильник `kid_count` відсутній, а зміщення до поля `DataSize` починається одразу після `SystemID`. У версії 1 між ними розташовано 4 байти кількості ключів та масив `KID`.

Нижче наведено паралельну реалізацію високопродуктивного парсера боксу PSSH мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#if defined(_WIN32)
  #include <winsock2.h>
#else
  #include <arpa/inet.h>
#endif

/* Двійкова структура розібраного PSSH-боксу */
typedef struct {
    uint8_t  version;
    uint8_t  system_id[16];
    uint32_t kid_count;
    uint8_t (*kids)[16];       /* динамічний масив 16-байтових KID */
    uint32_t data_size;
    uint8_t *data;             /* непрозоре навантаження DRM */
} pssh_box_t;

/* Читання 32-бітного uint у форматі big-endian */
static inline uint32_t read_be32(const uint8_t *buf) {
    return ((uint32_t)buf[0] << 24) |
           ((uint32_t)buf[1] << 16) |
           ((uint32_t)buf[2] <<  8) |
           ((uint32_t)buf[3]);
}

/**
 * Парсер боксу pssh відповідно до стандарту ISO/IEC 23001-7.
 * Повертає true у разі успішного розбору, false при пошкодженні даних.
 */
bool parse_pssh_box(const uint8_t *raw_buf, size_t buf_len, pssh_box_t *out_box) {
    if (!raw_buf || !out_box || buf_len < 32) {
        return false;
    }

    memset(out_box, 0, sizeof(*out_box));

    size_t offset = 0;
    uint32_t box_size = read_be32(raw_buf + offset);
    offset += 4;

    if (box_size > buf_len || box_size < 32) {
        return false;
    }

    /* Перевірка FourCC типу боксу: 'pssh' == 0x70737368 */
    if (memcmp(raw_buf + offset, "pssh", 4) != 0) {
        return false;
    }
    offset += 4;

    out_box->version = raw_buf[offset];
    offset += 1;

    /* 3 байти flags (пропускаємо) */
    offset += 3;

    /* 16 байтів SystemID */
    memcpy(out_box->system_id, raw_buf + offset, 16);
    offset += 16;

    if (out_box->version == 1) {
        if (offset + 4 > box_size) return false;
        out_box->kid_count = read_be32(raw_buf + offset);
        offset += 4;

        if (offset + (out_box->kid_count * 16) > box_size) {
            return false;
        }

        if (out_box->kid_count > 0) {
            out_box->kids = (uint8_t(*)[16])malloc(out_box->kid_count * 16);
            if (!out_box->kids) return false;
            memcpy(out_box->kids, raw_buf + offset, out_box->kid_count * 16);
            offset += out_box->kid_count * 16;
        }
    } else {
        out_box->kid_count = 0;
        out_box->kids = NULL;
    }

    if (offset + 4 > box_size) {
        free(out_box->kids);
        return false;
    }

    out_box->data_size = read_be32(raw_buf + offset);
    offset += 4;

    if (offset + out_box->data_size > box_size) {
        free(out_box->kids);
        return false;
    }

    if (out_box->data_size > 0) {
        out_box->data = (uint8_t *)malloc(out_box->data_size);
        if (!out_box->data) {
            free(out_box->kids);
            return false;
        }
        memcpy(out_box->data, raw_buf + offset, out_box->data_size);
    }

    return true;
}

void free_pssh_box(pssh_box_t *box) {
    if (box) {
        free(box->kids);
        free(box->data);
        memset(box, 0, sizeof(*box));
    }
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <array>
#include <optional>
#include <cstdint>
#include <cstring>

#if defined(_WIN32)
  #include <winsock2.h>
#else
  #include <arpa/inet.h>
#endif

namespace drm {

struct PsshBox {
    uint8_t version{0};
    std::array<uint8_t, 16> system_id{};
    std::vector<std::array<uint8_t, 16>> kids;
    std::vector<uint8_t> data;
};

class PsshParser {
public:
    static std::optional<PsshBox> parse(std::span<const uint8_t> bytes) {
        if (bytes.size() < 32) {
            return std::nullopt;
        }

        size_t offset = 0;
        uint32_t box_size = read_be32(bytes.subspan(offset, 4));
        offset += 4;

        if (box_size > bytes.size() || box_size < 32) {
            return std::nullopt;
        }

        // Перевірка FourCC: 'pssh'
        if (std::memcmp(bytes.data() + offset, "pssh", 4) != 0) {
            return std::nullopt;
        }
        offset += 4;

        PsshBox box;
        box.version = bytes[offset++];
        offset += 3; // flags

        std::memcpy(box.system_id.data(), bytes.data() + offset, 16);
        offset += 16;

        if (box.version == 1) {
            if (offset + 4 > box_size) return std::nullopt;
            uint32_t kid_count = read_be32(bytes.subspan(offset, 4));
            offset += 4;

            if (offset + (static_cast<size_t>(kid_count) * 16) > box_size) {
                return std::nullopt;
            }

            box.kids.resize(kid_count);
            for (uint32_t i = 0; i < kid_count; ++i) {
                std::memcpy(box.kids[i].data(), bytes.data() + offset, 16);
                offset += 16;
            }
        }

        if (offset + 4 > box_size) return std::nullopt;
        uint32_t data_size = read_be32(bytes.subspan(offset, 4));
        offset += 4;

        if (offset + data_size > box_size) return std::nullopt;

        box.data.resize(data_size);
        if (data_size > 0) {
            std::memcpy(box.data.data(), bytes.data() + offset, data_size);
        }

        return box;
    }

private:
    static inline uint32_t read_be32(std::span<const uint8_t, 4> s) {
        return (static_cast<uint32_t>(s[0]) << 24) |
               (static_cast<uint32_t>(s[1]) << 16) |
               (static_cast<uint32_t>(s[2]) <<  8) |
               (static_cast<uint32_t>(s[3]));
    }
};

} // namespace drm
```
:::

---

## 3. Криптографічний механізм загортання ключів (AES Key Wrap — RFC 3394)

Коли сервер ліцензій ухвалює рішення видати 128-бітний симетричний ключ контенту `K_content`, він не може передати його клієнту у відкритому вигляді. Навіть захищене з'єднання TLS є недостатнім, оскільки сесія TLS термінується в звичайному мережевому стеку операційної системи (користувацький простір або ядро ОС), звідки зловмисник із правами адміністратора може зчитати байти ключа з оперативної пам'яті.

Тому сервер упаковує `K_content` у спеціальний криптографічний конверт за допомогою стандарту **AES Key Wrap (KW)**, визначеного специфікаціями NIST SP 800-38F та RFC 3394. Ключ загортається на тимчасовому сесійному ключі `K_session` (Key Encryption Key, KEK), який попередньо узгоджується між сервером та апаратним модулем TEE пристрою.

### Математична сутність алгоритму AES Key Wrap

Алгоритм AES Key Wrap є детермінованою схемою шифрування з автентифікацією, розробленою спеціально для захисту криптографічних ключів без потреби передавати окремий вектор ініціалізації чи роздувати розмір блоку:
- Вхідний відкритий ключ розбивається на `n` 64-бітних блоків: `P = (R[1], R[2], ..., R[n])`. Для 128-бітного ключа AES `n = 2`.
- Початкове значення регістра `A` ініціалізується константою фіксованого вектора цілісності:
```
A[0] = 0xA6A6A6A6A6A6A6A6
```
- Виконується 6 послідовних раундів змішування (`j = 0 ... 5`). У кожному раунді для кожного блоку `i = 1 ... n`:
  1. Старші 64 біти `A` конкатенуються з поточним 64-бітним блоком `R[i]`, утворюючи 128-бітний блок: `B = AES_K(A || R[i])`.
  2. Нове значення `A` формується операцією XOR старших 64 бітів результату `B` зі змінною кроку `t = (n · j + i)`.
  3. Нове значення `R[i]` стає рівним молодшим 64 бітам `B`.
- Результатом загортання є `(n + 1)` 64-бітних блоків (для 128-бітного ключа — рівно 24 байти).

Під час розгортання в анклаві TEE після 6 раундів зворотного дешифрування виконується перевірка: якщо фінальне значення `A` точно дорівнює константі `0xA6A6A6A6A6A6A6A6`, ключ вважається цілісним та автентичним. Якщо хоча б один біт шифротексту було підроблено або змінено, перевірка провалюється, і TEE негайно знищує сесію.

Нижче наведено повну реалізацію алгоритму AES-128 Key Wrap мовами C та C++.

:::tabs
```c
#include <stdint.h>
#include <string.h>
#include <stdbool.h>

/* Початковий вектор (IV) за RFC 3394: 0xA6A6A6A6A6A6A6A6 */
static const uint8_t DEFAULT_IV[8] = { 0xA6, 0xA6, 0xA6, 0xA6, 0xA6, 0xA6, 0xA6, 0xA6 };

/* Зовнішня функція одиночного перетворення AES-128 (16 байтів in -> 16 байтів out) */
extern void aes128_encrypt_block(const uint8_t key[16], const uint8_t in[16], uint8_t out[16]);

/**
 * Загортання ключа контенту (AES Key Wrap, RFC 3394).
 * n: кількість 64-бітних блоків відкритого ключа (для AES-128 n = 2).
 * in_key: вхідний ключ довжиною n * 8 байтів (16 байтів).
 * out_wrapped: вихідний загорнутий блок довжиною (n + 1) * 8 байтів (24 байти).
 */
bool aes_key_wrap_128(const uint8_t kek[16], const uint8_t *in_key, size_t n, uint8_t *out_wrapped) {
    if (!kek || !in_key || !out_wrapped || n == 0) {
        return false;
    }

    uint8_t a[8];
    memcpy(a, DEFAULT_IV, 8);

    /* Масив блоків R[1]..R[n] */
    uint8_t r[n][8];
    for (size_t i = 0; i < n; ++i) {
        memcpy(r[i], in_key + (i * 8), 8);
    }

    /* 6 раундів змішування */
    for (uint32_t j = 0; j <= 5; ++j) {
        for (size_t i = 1; i <= n; ++i) {
            uint8_t b_in[16];
            uint8_t b_out[16];

            /* B = AES(K, A | R[i]) */
            memcpy(b_in, a, 8);
            memcpy(b_in + 8, r[i - 1], 8);

            aes128_encrypt_block(kek, b_in, b_out);

            /* A = MSB(64, B) ^ t */
            uint64_t t = (uint64_t)(n * j + i);
            memcpy(a, b_out, 8);
            for (int k = 0; k < 8; ++k) {
                a[7 - k] ^= (uint8_t)((t >> (k * 8)) & 0xFF);
            }

            /* R[i] = LSB(64, B) */
            memcpy(r[i - 1], b_out + 8, 8);
        }
    }

    /* Формування результату C = A | R[1] | ... | R[n] */
    memcpy(out_wrapped, a, 8);
    for (size_t i = 0; i < n; ++i) {
        memcpy(out_wrapped + 8 + (i * 8), r[i], 8);
    }

    return true;
}
```
```cpp
#include <array>
#include <span>
#include <cstdint>
#include <cstring>
#include <optional>

namespace drm::crypto {

// Фіксований IV для RFC 3394
constexpr std::array<uint8_t, 8> DEFAULT_IV = {
    0xA6, 0xA6, 0xA6, 0xA6, 0xA6, 0xA6, 0xA6, 0xA6
};

extern void aes128_encrypt_block(std::span<const uint8_t, 16> key,
                                 std::span<const uint8_t, 16> in,
                                 std::span<uint8_t, 16> out);

/**
 * Ідіоматичний C++20 Key Wrap для 128-бітного ключа контенту (видає 24 байти)
 */
std::optional<std::array<uint8_t, 24>> wrap_key_128(
    std::span<const uint8_t, 16> kek,
    std::span<const uint8_t, 16> plaintext_key)
{
    constexpr size_t N = 2; // 2 блоки по 64 біти = 128 біт
    std::array<uint8_t, 8> a = DEFAULT_IV;
    std::array<std::array<uint8_t, 8>, N> r{};

    std::memcpy(r[0].data(), plaintext_key.data(), 8);
    std::memcpy(r[1].data(), plaintext_key.data() + 8, 8);

    for (uint32_t j = 0; j <= 5; ++j) {
        for (size_t i = 1; i <= N; ++i) {
            std::array<uint8_t, 16> b_in{};
            std::array<uint8_t, 16> b_out{};

            std::memcpy(b_in.data(), a.data(), 8);
            std::memcpy(b_in.data() + 8, r[i - 1].data(), 8);

            aes128_encrypt_block(kek, b_in, b_out);

            uint64_t t = static_cast<uint64_t>(N * j + i);
            std::memcpy(a.data(), b_out.data(), 8);
            for (int k = 0; k < 8; ++k) {
                a[7 - k] ^= static_cast<uint8_t>((t >> (k * 8)) & 0xFF);
            }

            std::memcpy(r[i - 1].data(), b_out.data() + 8, 8);
        }
    }

    std::array<uint8_t, 24> wrapped{};
    std::memcpy(wrapped.data(), a.data(), 8);
    std::memcpy(wrapped.data() + 8, r[0].data(), 8);
    std::memcpy(wrapped.data() + 16, r[1].data(), 8);

    return wrapped;
}

} // namespace drm::crypto
```
:::

---

## 4. Зворотне розгортання ключа контенту (AES Key Unwrap)

В анклаві TEE апаратний криптомодуль виконує операцію, дзеркальну до загортання: **AES Key Unwrap**. Модуль приймає 24-байтовий загорнутий шифротекст `C = (A, R[1], ..., R[n])` та 128-бітний ключ розпакування KEK (сесійний ключ `K_session`).

### Алгоритм зворотного перетворення

1. Значення регістра `A` ініціалізується першими 64 бітами шифротексту: `A = C[0 ... 7]`.
2. Блоки `R[1] ... R[n]` завантажуються з решти шифротексту.
3. Виконується 6 зворотних раундів (`j = 5 ... 0`), де для кожного `i = n ... 1`:
   - Змінна кроку обчислюється як `t = n · j + i`.
   - Старші 64 біти `A` модифікуються операцією XOR зі значенням `t`: `A' = A ⊕ t`.
   - Формується 128-бітний вхідний блок `(A' || R[i])`.
   - Виконується одиночне розшифрування блоку AES: `B = AES_inv_K(A' || R[i])`.
   - Регістр `A` оновлюється значенням старших 64 бітів `B`: `A = MSB(64, B)`.
   - Блок `R[i]` стає рівним молодшим 64 бітам `B`: `R[i] = LSB(64, B)`.
4. **Перевірка цілісності**: Регістр `A` порівнюється з константою `0xA6A6A6A6A6A6A6A6`. Якщо значення збігається, блоки `R[1] ... R[n]` конкатенуються у відкритий ключ `K_content`. Якщо хоча б один біт відрізняється, функція повертає помилку автентифікації, а розшифровані дані негайно стираються з пам'яті.

Нижче наведено реалізацію перевірки та розгортання мовами C та C++.

:::tabs
```c
/* Зовнішня функція одиночного дешифрування AES-128 (16 байтів in -> 16 байтів out) */
extern void aes128_decrypt_block(const uint8_t key[16], const uint8_t in[16], uint8_t out[16]);

/**
 * Розгортання ключа контенту (AES Key Unwrap, RFC 3394).
 * in_wrapped: вхідний загорнутий блок довжиною (n + 1) * 8 байтів (24 байти).
 * n: кількість 64-бітних блоків відкритого ключа (для AES-128 n = 2).
 * out_key: вихідний відкритий ключ довжиною n * 8 байтів (16 байтів).
 * Повертає true, якщо цілісність підтверджено (IV збігся), false при збої.
 */
bool aes_key_unwrap_128(const uint8_t kek[16], const uint8_t *in_wrapped, size_t n, uint8_t *out_key) {
    if (!kek || !in_wrapped || !out_key || n == 0) {
        return false;
    }

    uint8_t a[8];
    memcpy(a, in_wrapped, 8);

    uint8_t r[n][8];
    for (size_t i = 0; i < n; ++i) {
        memcpy(r[i], in_wrapped + 8 + (i * 8), 8);
    }

    /* 6 зворотних раундів */
    for (int32_t j = 5; j >= 0; --j) {
        for (size_t i = n; i >= 1; --i) {
            uint64_t t = (uint64_t)(n * j + i);
            for (int k = 0; k < 8; ++k) {
                a[7 - k] ^= (uint8_t)((t >> (k * 8)) & 0xFF);
            }

            uint8_t b_in[16];
            uint8_t b_out[16];

            /* B = AES_inv(K, (A ^ t) | R[i]) */
            memcpy(b_in, a, 8);
            memcpy(b_in + 8, r[i - 1], 8);

            aes128_decrypt_block(kek, b_in, b_out);

            memcpy(a, b_out, 8);
            memcpy(r[i - 1], b_out + 8, 8);
        }
    }

    /* Перевірка вектора цілісності IV */
    if (memcmp(a, DEFAULT_IV, 8) != 0) {
        /* Збій цілісності: очищаємо пам'ять і повертаємо помилку */
        memset(r, 0, sizeof(r));
        return false;
    }

    for (size_t i = 0; i < n; ++i) {
        memcpy(out_key + (i * 8), r[i], 8);
    }

    return true;
}
```
```cpp
namespace drm::crypto {

extern void aes128_decrypt_block(std::span<const uint8_t, 16> key,
                                 std::span<const uint8_t, 16> in,
                                 std::span<uint8_t, 16> out);

/**
 * Ідіоматичний C++20 Key Unwrap для 128-бітного ключа (приймає 24 байти, видає 16)
 */
std::optional<std::array<uint8_t, 16>> unwrap_key_128(
    std::span<const uint8_t, 16> kek,
    std::span<const uint8_t, 24> wrapped_key)
{
    constexpr size_t N = 2;
    std::array<uint8_t, 8> a{};
    std::memcpy(a.data(), wrapped_key.data(), 8);

    std::array<std::array<uint8_t, 8>, N> r{};
    std::memcpy(r[0].data(), wrapped_key.data() + 8, 8);
    std::memcpy(r[1].data(), wrapped_key.data() + 16, 8);

    for (int32_t j = 5; j >= 0; --j) {
        for (size_t i = N; i >= 1; --i) {
            uint64_t t = static_cast<uint64_t>(N * j + i);
            for (int k = 0; k < 8; ++k) {
                a[7 - k] ^= static_cast<uint8_t>((t >> (k * 8)) & 0xFF);
            }

            std::array<uint8_t, 16> b_in{};
            std::array<uint8_t, 16> b_out{};

            std::memcpy(b_in.data(), a.data(), 8);
            std::memcpy(b_in.data() + 8, r[i - 1].data(), 8);

            aes128_decrypt_block(kek, b_in, b_out);

            std::memcpy(a.data(), b_out.data(), 8);
            std::memcpy(r[i - 1].data(), b_out.data() + 8, 8);
        }
    }

    // Перевірка вектора цілісності
    if (a != DEFAULT_IV) {
        return std::nullopt; // Підроблені або пошкоджені дані
    }

    std::array<uint8_t, 16> plaintext_key{};
    std::memcpy(plaintext_key.data(), r[0].data(), 8);
    std::memcpy(plaintext_key.data() + 8, r[1].data(), 8);

    return plaintext_key;
}

} // namespace drm::crypto
```
:::

---

## 5. Обслуговування офлайн-ліцензій (`persistent-license`)

Коли мобільний або настільний застосунок дозволяє користувачеві завантажувати фільми для автономного перегляду в дорозі або під час подорожей літаком, клієнтський конвеєр перемикається в режим довготривалого зберігання ліцензій.

### Особливості режиму збереження стану

1. **Конфігурація `persistentState: "required"`**: Під час запиту `requestMediaKeySystemAccess()` плеєр зобов'язаний вимагати підтримку енергонезалежного сховища ліцензій.
2. **Тип сесії `"persistent-license"`**: Замість тимчасової сесії створюється постійна: `mediaKeys.createSession("persistent-license")`.
3. **Збереження ідентифікатора сесії**: Після успішного виклику `session.update(licenseData)` значення `session.sessionId` зберігається в локальній базі даних (наприклад, IndexedDB або SQLite).
4. **Автономне відновлення сесії**: Коли користувач запускає відтворення за відсутності мережевого з'єднання, код не генерує новий запит через `generateRequest()`, а викликає `session.load(savedSessionId)`. Модуль CDM зчитує зашифрований стан із захищеного сховища пристрою, перевіряє системний таймер та активує ключі без жодного звернення до сервера.
5. **Вивільнення ліцензії (`session.remove()`)**: Коли користувач видаляє завантажений фільм або термін його оренди спливає, застосунок викликає `session.remove()`. CDM видаляє ключі з локальної пам'яті та генерує повідомлення `messageType: "license-release"`. Це повідомлення надсилається на сервер ліцензій під час наступного виходу в онлайн для повернення слота завантаження.

---

## 6. Серверний ліцензійний проксі на Python та інтеграція з KMS

Для повноцінної роботи системи ліцензування між браузером користувача та спеціалізованим сховищем ключів (Key Management System, KMS) розгортається сервіс License Proxy. Його обов'язки:
1. Перевірити автентичність користувача (JWT-токен або сесійні cookies).
2. Визначити тарифний план та бізнес-правила: максимальну дозволену роздільну здатність (SD, HD, 4K UHD), час оренди та вимоги до захисту цифрового виводу (HDCP).
3. Передати License Challenge від клієнта до ядра DRM KMS разом із параметрами політики.
4. Отримати від KMS запечатаний License Response та повернути його клієнту.

### Стандартизовані протоколи взаємодії з KMS (SPEKE та CPIX)

У промислових системах потокового відео (OTT) сервер ліцензій рідко зберігає базу симетричних ключів безпосередньо в коді проксі. Замість цього проксі зв'язується з централізованим HSM (Hardware Security Module) або хмарним KMS через стандартизовані інтерфейси:
- **CPIX (Content Protection Information Exchange Format, DASH-IF)**: XML-специфікація для безпечного обміну ключами `K_content`, ідентифікаторами `KID`, сертифікатами та правилами шифрування між пакувальником, кодером та DRM-серверами.
- **SPEKE (Secure Preshared Key Exchange, AWS / SMPTE 2073-1)**: REST-протокол на базі автентифікації AWS SigV4, що дозволяє динамічно запитувати ключі контенту та генерувати готові PSSH-бокси в режимі реального часу.

Нижче наведено реалізацію асинхронного мікросервісу на базі `aiohttp`.

```python
"""
License Proxy Server: Перевірка JWT та маршрутизація запиту до KMS.
"""
from aiohttp import web
import jwt
import hmac
import hashlib
import os

JWT_SECRET = os.environ.get("DRM_JWT_SECRET", "super-secret-key-123")
KMS_INTERNAL_URL = "http://kms.internal.service/api/v1/license"

async def handle_license_request(request: web.Request) -> web.Response:
    # 1. Валідація заголовка авторизації
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return web.Response(status=401, text="Відсутній або некоректний токен авторизації")

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        has_active_subscription = payload.get("active_sub", False)
        max_allowed_resolution = payload.get("max_res", "1080p")
    except jwt.PyJWTError as e:
        return web.Response(status=403, text=f"Помилка перевірки токена: {str(e)}")

    if not has_active_subscription:
        return web.Response(status=402, text="Підписку користувача вичерпано")

    # 2. Отримання двійкового License Challenge від браузера
    challenge_bytes = await request.read()
    if not challenge_bytes:
        return web.Response(status=400, text="Порожнє тіло челенджу")

    # 3. Передача челенджу в ядро DRM KMS із додаванням бізнес-політик
    # Внутрішній KMS перевіряє сертифікат пристрою та загортає Content Key
    kms_headers = {
        "X-User-ID": str(user_id),
        "X-Max-Resolution": max_allowed_resolution,
        "X-Require-HDCP": "true" if max_allowed_resolution == "4k" else "false",
        "Content-Type": "application/octet-stream"
    }

    # Емуляція звернення до захищеного криптомодуля KMS
    # У бойовій системі тут викликається RPC/gRPC до Widevine KMS / PlayReady Server
    license_response_bytes = generate_mock_license_response(challenge_bytes, max_allowed_resolution)

    return web.Response(
        body=license_response_bytes,
        status=200,
        content_type="application/octet-stream"
    )

def generate_mock_license_response(challenge: bytes, max_res: str) -> bytes:
    # Структура відповіді: [4 байти Magic: 'LICR'] [1 байт Status] [Payload...]
    header = b"LICR\x00"
    policy_flag = b"\x02" if max_res == "4k" else b"\x01"
    # Додаємо псевдовипадковий загорнутий блок ключа
    wrapped_key = hashlib.sha256(challenge).digest()[:24]
    return header + policy_flag + wrapped_key

app = web.Application()
app.router.add_post("/api/drm/license", handle_license_request)

if __name__ == "__main__":
    web.run_app(app, port=8080)
```

---

## 7. Типові пастки та помилки налагодження

Під час інтеграції конвеєра EME та серверних обробників найчастіше виникають такі дефекти:

1. **Неправильний порядок ініціалізації `setMediaKeys`**:
   Якщо викликати `session.generateRequest()` до того, як `video.setMediaKeys(mediaKeys)` завершить свій проміс, браузер згенерує `InvalidStateError`. Прив'язка до елемента розмітки мусить завершитися першою, оскільки медіарушій браузера повинен заздалегідь знати, якому саме криптографічному контексту передавати розкодовані NAL-пакети.
2. **Блокування основного потоку в обробнику `encrypted`**:
   Подія `encrypted` виникає в процесі демультиплексування відео. Довгі синхронні операції або парсинг великих структур у головному потоці викликають затримку появи першого кадру (Time-to-First-Frame, TTFF). Усі мережеві запити ліцензій мають бути суворо асинхронними.
3. **Ігнорування підміни HDCP**:
   Якщо плеєр не підписаний на `keystatuseschange`, перемикання статусу ключа на `output-restricted` призведе до чорного екрана або безкінечного буферизування без повідомлення для користувача. Плеєр зобов'язаний динамічно знижувати якість потоку.
4. **Втрата оновлення сесії при ротації ключів (Key Rotation)**:
   Під час живих трансляцій (Live Streaming) нові бокси `pssh` надходять у кожному новому фрагменті медіа (бокс `moof`). Якщо плеєр щоразу створюватиме новий об'єкт `MediaKeySession`, пам'ять TEE швидко переповниться. Замість цього новий запит генерується в межах тієї самої активної сесії.
5. **Збої збереження сесії в IndexedDB та осиротілі ліцензії**:
   Якщо під час збереження `sessionId` у сховище браузера сталася помилка квоти пам'яті (`QuotaExceededError`) або збій транзакції, ліцензія лишається в захищеному сховищі CDM як «сирота» (Orphaned License), яку неможливо відновити чи вивільнити через API. Застосунок зобов'язаний обгортати оновлення сесії та запис у базу даних в єдину логічну транзакцію з обов'язковим викликом `session.remove()` у разі збою.
---

## 8. Стратегії повторних спроб (Retry Policy) та обробка збоїв

У реальних мережевих умовах мобільні пристрої часто зазнають короткочасних втрат зв'язку, перемикань між стільниковими вежами та Wi-Fi, а сервери ліцензій можуть повертати тимчасові помилки перевантаження (HTTP 429 Too Many Requests або HTTP 503 Service Unavailable).

### Правила побудови стійкого конвеєра

1. **Експоненційне відтермінування з джитером (Exponential Backoff with Jitter)**: Якщо мережевий запит до License Proxy зазнає невдачі, плеєр не повинен повторювати запит миттєво, щоб не створити лавиноподібне перевантаження («громоподібне стадо», Thundering Herd Problem). Пауза перед наступною спробою розраховується за формулою:
```
пауза = min(макс_пауза, базова_пауза · 2^(номер_спроби)) + випадковий_джитер
```
2. **Зіставлення з відеобуфером**: Доки тривають повторні спроби запиту ліцензії, відеоплеєр продовжує відтворювати вже завантажені та розшифровані секунди з буфера `SourceBuffer`. Якщо буфер вичерпується до отримання ліцензії, плеєр переходить у стан очікування (Buffering) і показує індикатор завантаження, уникаючи фатального збою відтворення.
3. **Критичні помилки авторизації (HTTP 401 та 403)**: На відміну від мережевих помилок 5xx, помилки 401/403 вказують на недійсний токен або відсутність підписки. У цьому разі повторні спроби негайно припиняються, активна сесія дешифрування закривається через `session.close()`, а користувачеві виводиться інтерфейс оновлення підписки.
