# ⚙️ Реалізація наскрізного шифрування WebPush (RFC 8291)

Стандарт WebPush (RFC 8030) забезпечує доставку повідомлень у браузер через шлюзи третіх сторін (Google FCM, Mozilla Autopush, Apple Push Service). Оскільки проміжний шлюз є недовіреним посередником (*untrusted proxy*), він не повинен мати доступу до вмісту повідомлень користувача. Для забезпечення конфіденційності та автентичності стандарт **RFC 8291** визначає протокол наскрізного шифрування корисного навантаження за схемою `aes128gcm`.

У цьому проєкті реалізовано повний цикл шифрування навантаження на сервері застосунків: генерація ефемерних ключів, виведення сесійних ключів через HKDF, формування бінарного кадру `aes128gcm`, підготовка тіла для HTTP POST-запиту та перевірка результатів за еталонними векторами.

---

## 1. Архітектура та математична схема шифрування

Шифрування за стандартом RFC 8291 базується на комбінації асиметричного обміну ключами Діффі–Геллмана на еліптичній кривій NIST P-256 (secp256r1), двоетапної функції виведення ключів на базі HMAC (HKDF, RFC 5869) з геш-функцією SHA-256 та симетричного автентифікованого шифрування AES-128-GCM.

### Чому шлюз не може розшифрувати навантаження
Під час створення підписки браузер генерує пару ключів на кривій NIST P-256: закритий ключ зберігається в захищеному сховищі браузера (IndexedDB / NSS profile), а відкритий ключ `client_p256dh` разом із випадковим секретом `client_auth` передається серверу застосунку.

Сервер застосунку генерує власну одноразову ефемерну пару ключів `(server_eph_priv, server_eph_pub)` для кожного окремого повідомлення. Спільний секрет Діффі–Геллмана `ECDH(server_eph_priv, client_p256dh)` може обчислити лише сервер застосунку та цільовий браузер. Жоден проміжний вузол (включно зі шлюзом push-служби або інтернет-провайдером), знаючи відкриті ключі обох сторін, не здатен відновити цей секрет без знання закритого ключа клієнта.

### Вхідні параметри від клієнта (PushSubscription)
1. **`client_p256dh` (65 байтів):** Публічний ключ браузера у нестисненому форматі точки еліптичної кривої: `0x04 || X (32 B) || Y (32 B)`.
2. **`client_auth` (16 байтів):** Випадковий секрет автентифікації клієнта (*Authentication Secret*), що запобігає атакам на підміну відкритого ключа.
3. **`plaintext`:** Відкритий текст повідомлення у форматі UTF-8 (зазвичай серіалізований JSON-рядок).

### Послідовність етапів криптографічного перетворення

```
1. Генерація ефемерної пари ключів сервера:
   (server_eph_priv, server_eph_pub) на кривій NIST P-256

2. Обчислення спільного секрету Діффі–Геллмана (ECDH):
   ecdh_secret = ECDH(server_eph_priv, client_p256dh)      [32 байти]

3. Двоетапне виведення вхідного матеріалу ключів (IKM) з урахуванням auth secret:
   prk_key  = HKDF-Extract(salt = client_auth, ikm = ecdh_secret)
   key_info = "WebPush: info\0" || client_p256dh || server_eph_pub
   ikm      = HKDF-Expand(prk = prk_key, info = key_info, len = 32)

4. Генерація випадкової солі повідомлення:
   salt = RandomBytes(16)

5. Виведення сесійного ключа шифрування (CEK) та одноразового вектора (Nonce):
   prk_main   = HKDF-Extract(salt = salt, ikm = ikm)
   cek_info   = "Content-Encoding: aes128gcm\0"
   nonce_info = "Content-Encoding: nonce\0"
   CEK        = HKDF-Expand(prk = prk_main, info = cek_info, len = 16)
   Nonce      = HKDF-Expand(prk = prk_main, info = nonce_info, len = 12)

6. Доповнення відкритого тексту (Padding):
   padded_text = plaintext || 0x02                         [0x02 — маркер кінця останнього блоку]

7. Автентифіковане шифрування AES-128-GCM:
   ciphertext, auth_tag = AES_128_GCM_Encrypt(key = CEK, iv = Nonce, data = padded_text)
```

### Формат бінарного кадру `aes128gcm`

Результат шифрування пакується у стандартизований бінарний заголовок і надсилається як `application/octet-stream`:

```
+---------------+----------------+----------------+------------------+---------------------+
|  salt (16 B)  |   rs (4 B)     |  idlen (1 B)   | keyid (65 B)     | ciphertext + tag    |
|               |  (Record Size) |  (довжина pub) | (server_eph_pub) | (змінна довжина)    |
+---------------+----------------+----------------+------------------+---------------------+
```

- `salt`: 16 байтів випадкової криптографічної солі повідомлення;
- `rs`: Розмір запису в байтах (4 байти Big-Endian, типове значення `4096` = `0x00001000`);
- `idlen`: Довжина ідентифікатора ключа (1 байт, значення `65` = `0x41` для нестисненої точки P-256);
- `keyid`: 65 байтів нестисненого відкритого ключа `server_eph_pub`;
- `ciphertext + tag`: Зашифровані дані відкритого тексту, до яких додано 16-байтний тег автентичності GCM.

---

## 2. Реалізація шифрування (C++ та TypeScript)

Нижче наведено промислові реалізації повного циклу шифрування RFC 8291.
- У вкладці C++ використано сучасний криптографічний інтерфейс OpenSSL 3.0 (`EVP_PKEY`, `EVP_KDF`, `EVP_CIPHER`) із суворим RAII-керуванням дескрипторами та безпечною роботою з пам'яттю через `std::span` та `std::vector<uint8_t>`.
- У вкладці TypeScript використано вбудований модуль `crypto` середовища Node.js без зовнішніх npm-залежностей.

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <memory>
#include <span>
#include <stdexcept>
#include <cstring>
#include <openssl/evp.h>
#include <openssl/ec.h>
#include <openssl/kdf.h>
#include <openssl/core_names.h>
#include <openssl/rand.h>

// RAII обгортки для структур OpenSSL
struct EvpPkeyDeleter { void operator()(EVP_PKEY* p) const { EVP_PKEY_free(p); } };
struct EvpPkeyCtxDeleter { void operator()(EVP_PKEY_CTX* p) const { EVP_PKEY_CTX_free(p); } };
struct EvpCipherCtxDeleter { void operator()(EVP_CIPHER_CTX* p) const { EVP_CIPHER_CTX_free(p); } };
struct EvpKdfCtxDeleter { void operator()(EVP_KDF_CTX* p) const { EVP_KDF_CTX_free(p); } };

using ScopedEVP_PKEY = std::unique_ptr<EVP_PKEY, EvpPkeyDeleter>;
using ScopedEVP_PKEY_CTX = std::unique_ptr<EVP_PKEY_CTX, EvpPkeyCtxDeleter>;
using ScopedEVP_CIPHER_CTX = std::unique_ptr<EVP_CIPHER_CTX, EvpCipherCtxDeleter>;
using ScopedEVP_KDF_CTX = std::unique_ptr<EVP_KDF_CTX, EvpKdfCtxDeleter>;

class WebPushEncryptor {
public:
    // Шифрує відкритий текст для клієнта за стандартом RFC 8291
    static std::vector<uint8_t> encrypt(
        std::span<const uint8_t> client_p256dh,
        std::span<const uint8_t> client_auth,
        std::string_view plaintext,
        uint32_t record_size = 4096)
    {
        if (client_p256dh.size() != 65 || client_p256dh[0] != 0x04) {
            throw std::invalid_argument("Некоректний публічний ключ клієнта (має бути 65 байтів uncompressed)");
        }
        if (client_auth.size() != 16) {
            throw std::invalid_argument("Секрет auth має мати довжину рівно 16 байтів");
        }

        // 1. Генерація ефемерної пари ключів сервера (NIST P-256)
        ScopedEVP_PKEY_CTX gen_ctx(EVP_PKEY_CTX_new_id(EVP_PKEY_EC, nullptr));
        if (!gen_ctx || EVP_PKEY_keygen_init(gen_ctx.get()) <= 0) {
            throw std::runtime_error("Помилка ініціалізації генератора ключів EC");
        }
        if (EVP_PKEY_CTX_set_ec_paramgen_curve_nid(gen_ctx.get(), NID_X9_62_prime256v1) <= 0) {
            throw std::runtime_error("Помилка вибору кривої P-256");
        }
        EVP_PKEY* raw_server_key = nullptr;
        if (EVP_PKEY_keygen(gen_ctx.get(), &raw_server_key) <= 0) {
            throw std::runtime_error("Помилка генерації ефемерного ключа сервера");
        }
        ScopedEVP_PKEY server_key(raw_server_key);

        // Експорт публічного ключа сервера (65 байтів)
        std::vector<uint8_t> server_pub(65);
        size_t server_pub_len = 65;
        if (EVP_PKEY_get_octet_string_param(server_key.get(), OSSL_PKEY_PARAM_PUB_KEY,
                                            server_pub.data(), server_pub.size(), &server_pub_len) <= 0) {
            throw std::runtime_error("Помилка експорту публічного ключа сервера");
        }

        // 2. Імпорт публічного ключа клієнта
        ScopedEVP_PKEY_CTX peer_ctx(EVP_PKEY_CTX_new_id(EVP_PKEY_EC, nullptr));
        EVP_PKEY_paramgen_init(peer_ctx.get());
        EVP_PKEY_CTX_set_ec_paramgen_curve_nid(peer_ctx.get(), NID_X9_62_prime256v1);
        EVP_PKEY* raw_peer_params = nullptr;
        EVP_PKEY_paramgen(peer_ctx.get(), &raw_peer_params);
        ScopedEVP_PKEY peer_params(raw_peer_params);

        EVP_PKEY* raw_peer_key = nullptr;
        ScopedEVP_PKEY_CTX import_ctx(EVP_PKEY_CTX_new_from_pkey(nullptr, peer_params.get(), nullptr));
        if (!import_ctx || EVP_PKEY_fromdata_init(import_ctx.get()) <= 0) {
            throw std::runtime_error("Помилка ініціалізації імпорту ключа клієнта");
        }

        OSSL_PARAM params[] = {
            OSSL_PARAM_construct_utf8_string(OSSL_PKEY_PARAM_GROUP_NAME, const_cast<char*>("prime256v1"), 0),
            OSSL_PARAM_construct_octet_string(OSSL_PKEY_PARAM_PUB_KEY, const_cast<uint8_t*>(client_p256dh.data()), client_p256dh.size()),
            OSSL_PARAM_construct_end()
        };
        if (EVP_PKEY_fromdata(import_ctx.get(), &raw_peer_key, EVP_PKEY_PUBLIC_KEY, params) <= 0) {
            throw std::runtime_error("Помилка імпорту точки відкритого ключа клієнта");
        }
        ScopedEVP_PKEY peer_key(raw_peer_key);

        // 3. Обчислення спільного секрету ECDH
        ScopedEVP_PKEY_CTX derive_ctx(EVP_PKEY_CTX_new(server_key.get(), nullptr));
        if (!derive_ctx || EVP_PKEY_derive_init(derive_ctx.get()) <= 0 ||
            EVP_PKEY_derive_set_peer(derive_ctx.get(), peer_key.get()) <= 0) {
            throw std::runtime_error("Помилка налаштування контексту ECDH");
        }
        size_t ecdh_secret_len = 0;
        EVP_PKEY_derive(derive_ctx.get(), nullptr, &ecdh_secret_len);
        std::vector<uint8_t> ecdh_secret(ecdh_secret_len);
        if (EVP_PKEY_derive(derive_ctx.get(), ecdh_secret.data(), &ecdh_secret_len) <= 0) {
            throw std::runtime_error("Помилка обчислення секрету ECDH");
        }

        // 4. Виведення IKM через HKDF з auth secret
        // key_info = "WebPush: info\0" || client_p256dh || server_pub
        std::vector<uint8_t> key_info;
        const std::string_view info_prefix = "WebPush: info";
        key_info.insert(key_info.end(), info_prefix.begin(), info_prefix.end());
        key_info.push_back(0x00);
        key_info.insert(key_info.end(), client_p256dh.begin(), client_p256dh.end());
        key_info.insert(key_info.end(), server_pub.begin(), server_pub.end());

        std::vector<uint8_t> ikm = hkdf_derive(client_auth, ecdh_secret, key_info, 32);

        // 5. Генерація випадкової солі (16 байтів)
        std::vector<uint8_t> salt(16);
        if (RAND_bytes(salt.data(), static_cast<int>(salt.size())) <= 0) {
            throw std::runtime_error("Помилка CSPRNG при генерації солі");
        }

        // 6. Виведення CEK (16 байтів) та Nonce (12 байтів)
        const std::string_view cek_info = "Content-Encoding: aes128gcm";
        std::vector<uint8_t> cek_info_bytes(cek_info.begin(), cek_info.end());
        cek_info_bytes.push_back(0x00);
        std::vector<uint8_t> cek = hkdf_derive(salt, ikm, cek_info_bytes, 16);

        const std::string_view nonce_info = "Content-Encoding: nonce";
        std::vector<uint8_t> nonce_info_bytes(nonce_info.begin(), nonce_info.end());
        nonce_info_bytes.push_back(0x00);
        std::vector<uint8_t> nonce = hkdf_derive(salt, ikm, nonce_info_bytes, 12);

        // 7. Формування доповнення відкритого тексту (Padding)
        // Додаємо байт 0x02 як розділювач останнього блоку
        std::vector<uint8_t> padded(plaintext.begin(), plaintext.end());
        padded.push_back(0x02);

        // 8. Шифрування AES-128-GCM
        ScopedEVP_CIPHER_CTX cipher_ctx(EVP_CIPHER_CTX_new());
        if (!cipher_ctx || EVP_EncryptInit_ex(cipher_ctx.get(), EVP_aes_128_gcm(), nullptr, nullptr, nullptr) <= 0) {
            throw std::runtime_error("Помилка ініціалізації шифру AES-128-GCM");
        }
        if (EVP_CIPHER_CTX_ctrl(cipher_ctx.get(), EVP_CTRL_GCM_SET_IVLEN, static_cast<int>(nonce.size()), nullptr) <= 0) {
            throw std::runtime_error("Помилка встановлення довжини Nonce");
        }
        if (EVP_EncryptInit_ex(cipher_ctx.get(), nullptr, nullptr, cek.data(), nonce.data()) <= 0) {
            throw std::runtime_error("Помилка передачі ключа та IV в AES-GCM");
        }

        std::vector<uint8_t> ciphertext(padded.size());
        int out_len = 0;
        if (EVP_EncryptUpdate(cipher_ctx.get(), ciphertext.data(), &out_len, padded.data(), static_cast<int>(padded.size())) <= 0) {
            throw std::runtime_error("Помилка шифрування блоку даних");
        }
        int final_len = 0;
        if (EVP_EncryptFinal_ex(cipher_ctx.get(), ciphertext.data() + out_len, &final_len) <= 0) {
            throw std::runtime_error("Помилка фіналізації шифру");
        }

        std::vector<uint8_t> tag(16);
        if (EVP_CIPHER_CTX_ctrl(cipher_ctx.get(), EVP_CTRL_GCM_GET_TAG, static_cast<int>(tag.size()), tag.data()) <= 0) {
            throw std::runtime_error("Помилка отримання тегу автентичності GCM");
        }

        // 9. Складання фінального бінарного кадру aes128gcm
        // [salt (16 B)] || [rs (4 B)] || [idlen = 65 (1 B)] || [server_pub (65 B)] || [ciphertext] || [tag (16 B)]
        std::vector<uint8_t> payload;
        payload.reserve(16 + 4 + 1 + 65 + ciphertext.size() + tag.size());

        payload.insert(payload.end(), salt.begin(), salt.end());

        // Запис record_size як 32-бітного числа Big-Endian
        payload.push_back(static_cast<uint8_t>((record_size >> 24) & 0xFF));
        payload.push_back(static_cast<uint8_t>((record_size >> 16) & 0xFF));
        payload.push_back(static_cast<uint8_t>((record_size >> 8) & 0xFF));
        payload.push_back(static_cast<uint8_t>(record_size & 0xFF));

        payload.push_back(static_cast<uint8_t>(server_pub.size())); // idlen = 65
        payload.insert(payload.end(), server_pub.begin(), server_pub.end());
        payload.insert(payload.end(), ciphertext.begin(), ciphertext.end());
        payload.insert(payload.end(), tag.begin(), tag.end());

        return payload;
    }

private:
    static std::vector<uint8_t> hkdf_derive(
        std::span<const uint8_t> salt,
        std::span<const uint8_t> ikm,
        std::span<const uint8_t> info,
        size_t out_len)
    {
        EVP_KDF* kdf = EVP_KDF_fetch(nullptr, "HKDF", nullptr);
        if (!kdf) throw std::runtime_error("HKDF алгоритм недоступний в OpenSSL");
        ScopedEVP_KDF_CTX kdf_ctx(EVP_KDF_CTX_new(kdf));
        EVP_KDF_free(kdf);

        OSSL_PARAM params[5];
        params[0] = OSSL_PARAM_construct_utf8_string(OSSL_KDF_PARAM_DIGEST, const_cast<char*>("SHA256"), 0);
        params[1] = OSSL_PARAM_construct_octet_string(OSSL_KDF_PARAM_SALT, const_cast<uint8_t*>(salt.data()), salt.size());
        params[2] = OSSL_PARAM_construct_octet_string(OSSL_KDF_PARAM_KEY, const_cast<uint8_t*>(ikm.data()), ikm.size());
        params[3] = OSSL_PARAM_construct_octet_string(OSSL_KDF_PARAM_INFO, const_cast<uint8_t*>(info.data()), info.size());
        params[4] = OSSL_PARAM_construct_end();

        std::vector<uint8_t> out(out_len);
        if (EVP_KDF_derive(kdf_ctx.get(), out.data(), out.size(), params) <= 0) {
            throw std::runtime_error("Помилка виконання HKDF");
        }
        return out;
    }
};
```
```ts
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
```
:::

---

## 3. Дешифрування в браузері (Service Worker API)

На стороні клієнтського браузера отримане повідомлення обробляється фоновим скриптом Service Worker. Браузерний рушій (Chromium Blink, Gecko або WebKit) виконує симетричне дешифрування на рівні C++ коду ядра до виклику JavaScript, автоматично перевіряючи тег автентичності GCM.

Обробник події `push` отримує вже повністю розшифрований відкритий текст через об'єкт `event.data`:

```ts
// service-worker.ts — клієнтський обробник у браузері
self.addEventListener('push', (event: PushEvent) => {
  if (!event.data) {
    console.warn('Отримано тихий пуш без корисного навантаження');
    return;
  }

  // Отримання розшифрованого JSON-об'єкта
  const payload = event.data.json();

  const title = payload.title || 'Нове сповіщення';
  const options: NotificationOptions = {
    body: payload.body,
    icon: payload.icon || '/icons/notification-192.png',
    badge: '/icons/badge-72.png',
    data: {
      url: payload.url || '/'
    }
  };

  // Показ системного сповіщення через Notification API
  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});
```

Якщо під час транспортування хоча б один байт шифротексту було спотворено, або якщо сервер використав неправильний публічний ключ клієнта, автентифікація AES-GCM провалюється: браузер мовчки відкидає зіпсований пакет і взагалі не генерує подію `push` у Service Worker.

---

## 4. Розбір крайових випадків та типові пастки реалізації

При впровадженні стандарту RFC 8291 розробники найчастіше припускаються критичних помилок у п'яти ключових місцях:

1. **Повторне використання ефемерних ключів сервера (Nonce-Reuse Disaster):**
   У криптографії алгоритм AES-GCM є вкрай чутливим до повторного використання пари `(Key, IV)`. Якщо сервер оптимізує ресурси й згенерує один ефемерний ключ на декілька повідомлень або згенерує однакову сіль `salt`, зловмисник зможе відновити відкритий текст обох повідомлень за допомогою операції XOR та обчислити ключ автентифікації GHASH. **Правило:** кожне push-повідомлення вимагає виклику криптографічно стійкого генератора псевдовипадкових чисел (CSPRNG) для створення нової пари ключів EC та нової солі.

2. **Порядок передачі ключів у `key_info`:**
   Стандарт RFC 8291 (§3.2) вимагає суворого порядку конкатенації:
   `"WebPush: info\0" || client_public_key (65 B) || server_public_key (65 B)`.
   Якщо поміняти ключі місцями або пропустити нульовий байт `\0`, виведений IKM буде відрізнятися від обчисленого браузером, і спроба дешифрування в обробнику Service Worker завершиться винятком `DOMException: Decryption failed`.

3. **Формат відкритого ключа (Compression):**
   Публічні ключі еліптичних кривих бувають стисненими (33 байти, префікс `0x02` або `0x03`) та нестисненими (65 байтів, префікс `0x04`). Стандарт WebPush вимагає **виключно нестисненого формату**. Якщо криптографічна бібліотека повертає стиснену точку, її необхідно розгорнути перед розрахунком `key_info` та записом у заголовок кадру.

4. **Маркер кінця блоку (Padding Delimiter):**
   У застарілому драфті `aesgcm` навантаження вимагало додавання довжини паддінгу на початку блоку. У фінальному стандарті RFC 8291 `aes128gcm` застосовується суфіксний маркер:
   - `0x02` — останній або єдиний запис повідомлення;
   - `0x01` — проміжний блок запису (при фрагментації на декілька блоків `rs`);
   - `0x00` — байти порожнього заповнення (padding) для маскування реального розміру навантаження від аналізу мережевого трафіку.

5. **Розмір запису `rs` (Record Size):**
   Мінімально допустимий розмір запису становить 18 байтів (16 байтів тегу + 1 байт навантаження + 1 байт маркера). За замовчуванням більшість браузерних реалізацій очікують розмір блоку `4096` байтів (`0x00001000`). Якщо загальний розмір шифротексту перевищує `rs`, повідомлення має розбиватися на кілька послідовних кадрів, кожен із яких шифрується з власним лічильником у векторі Nonce.
