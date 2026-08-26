# 📋 Специфікація OCI Distribution Spec: REST API, дескриптори та заголовки

Специфікація **OCI Distribution Specification** визначає загальноприйнятий мережевий протокол взаємодії між клієнтами контейнеризації (containerd, CRI-O, Podman, Docker, Skopeo, ORAS) та віддаленими реєстрами образів (OCI Registries). Протокол базується на безстановому REST поверх захищеного з'єднання HTTPS з обов'язковою адресацією за вмістом (Content-Addressable Storage — CAS) та механізмом Bearer-токенів автентифікації.

Нижче наведено повний системний довідник контрактів запитів, заголовків, кодів відповідей, форматів помилок, механізмів пагінації та специфікації типів медіа-вмісту (Media Types).

---

## 1. Базові типи медіа-вмісту (Media Types)

Кожен об'єкт, що передається або зберігається через OCI Distribution API, супроводжується обов'язковим заголовком `Content-Type`, який однозначно визначає його роль у дереві дескрипторів:

| Media Type | Опис сутності та призначення |
|---|---|
| `application/vnd.oci.image.index.v1+json` | Мультиархітектурний індекс (Image Index / Fat Manifest), що містить список маніфестів для різних ОС та архітектур процесорів |
| `application/vnd.oci.image.manifest.v1+json` | Маніфест конкретного образу: зв'язує дескриптор конфігурації (Config Descriptor) із масивом дескрипторів шарів (Layers) |
| `application/vnd.oci.image.config.v1+json` | JSON-документ конфігурації середовища виконання (змінні оточення `Env`, `Entrypoint`, `Cmd`, `rootfs.diff_ids`) |
| `application/vnd.oci.image.layer.v1.tar` | Нестиснутий tar-архів шару файлової системи (diff) |
| `application/vnd.oci.image.layer.v1.tar+gzip` | Шар файлової системи, стиснутий алгоритмом Gzip |
| `application/vnd.oci.image.layer.v1.tar+zstd` | Шар файлової системи, стиснутий алгоритмом Zstandard (Zstd) із підтримкою швидкої декомпресії |
| `application/vnd.oci.image.layer.nondistributable.v1.tar+gzip` | Нерозповсюджуваний шар (наприклад, ліцензійні базові шари Windows Base OS), який завантажується безпосередньо з серверів правовласника |
| `application/vnd.oci.empty.v1+json` | Порожній дескриптор для артефактів без шарів (OCI 1.1 Artifacts) |

---

## 2. Ендпоінти REST API та специфікація контрактів

### 2.1. Перевірка версії API та доступності реєстру
```http
GET /v2/
```
- **Призначення:** Базовий пінг для перевірки підтримки OCI Distribution API v2 та ініціалізації виклику автентифікації.
- **Успішна відповідь:** `200 OK`
- **Заголовки відповіді:**
  - `Docker-Distribution-API-Version: registry/2.0`
- **Відповідь без автентифікації:** `401 Unauthorized`
  - `Www-Authenticate: Bearer realm="https://auth.registry.io/token",service="registry.io",scope="repository:user/app:pull"`

---

### 2.2. Отримання маніфесту (Manifest Pull)
```http
GET /v2/<name>/manifests/<reference>
```
- **Параметри шляху:**
  - `<name>` — простір імен та ім'я репозиторію (наприклад, `library/ubuntu` або `myorg/backend`).
  - `<reference>` — змінний тег (наприклад, `latest`, `v1.2.0`) або незмінний криптографічний дайджест (наприклад, `sha256:7f3b1a98c5...`).
- **Обов'язкові заголовки запиту:**
  - `Accept: application/vnd.oci.image.manifest.v1+json, application/vnd.oci.image.index.v1+json, application/vnd.docker.distribution.manifest.v2+json`
  - `Authorization: Bearer <token>`
- **Успішна відповідь:** `200 OK`
- **Заголовки відповіді:**
  - `Content-Type: application/vnd.oci.image.manifest.v1+json`
  - `Docker-Content-Digest: sha256:7f3b1a98c5...` (канонічний SHA-256 хеш повернутого тіла маніфесту)
  - `Etag: "sha256:7f3b1a98c5..."`
- **Типові помилки:**
  - `404 Not Found` (`MANIFEST_UNKNOWN`) — репозиторій або вказаний тег/дайджест відсутній.

---

### 2.3. Перевірка існування маніфесту без передачі тіла
```http
HEAD /v2/<name>/manifests/<reference>
```
- **Призначення:** Швидка перевірка валідності локального кешу та отримання дайджесту через `Docker-Content-Digest` без передачі JSON-документа по мережі.
- **Успішна відповідь:** `200 OK`
- **Заголовки відповіді:** `Content-Length`, `Docker-Content-Digest`, `Content-Type`.

---

### 2.4. Завантаження маніфесту в реєстр (Manifest Push)
```http
PUT /v2/<name>/manifests/<reference>
```
- **Параметри шляху:** `<reference>` — тег або канонічний дайджест маніфесту.
- **Обов'язкові заголовки запиту:**
  - `Content-Type: application/vnd.oci.image.manifest.v1+json` (або `image.index.v1+json`)
- **Тіло запиту:** Канонічний JSON маніфесту OCI.
- **Успішна відповідь:** `201 Created`
- **Заголовки відповіді:**
  - `Location: /v2/<name>/manifests/<digest>`
  - `Docker-Content-Digest: sha256:...`
- **Типові помилки:**
  - `400 Bad Request` (`MANIFEST_INVALID`) — синтаксична помилка JSON або відсутність обов'язкових полів у дескрипторах.
  - `400 Bad Request` (`BLOB_UNKNOWN`) — маніфест посилається на шар, який ще не був завантажений у реєстр через Blob API.

---

### 2.5. Видалення маніфесту
```http
DELETE /v2/<name>/manifests/<reference>
```
- **Параметри шляху:** `<reference>` — виключно канонічний дайджест маніфесту `sha256:...` (видалення за тегом заборонено більшістю реєстрів задля безпеки).
- **Успішна відповідь:** `202 Accepted`

---

### 2.6. Завантаження бінарного блобу (Blob Pull: Layer / Config)
```http
GET /v2/<name>/blobs/<digest>
```
- **Параметри шляху:** `<digest>` — канонічний криптографічний хеш блобу у форматі `<algorithm>:<hex>` (наприклад, `sha256:3d4f56a...`).
- **Успішна відповідь (пряма віддача):** `200 OK`
  - `Content-Type: application/octet-stream` (або відповідний Media Type)
  - `Docker-Content-Digest: sha256:...`
  - `Content-Length: <bytes>`
  - Тіло: бінарний потік архіву або JSON-конфігурації.
- **Успішна відповідь (перенаправлення на об'єктне сховище S3/CDN):** `307 Temporary Redirect`
  - `Location: https://storage.googleapis.com/registry-blobs/sha256_3d4f56a...?signature=...`
  - Клієнт зобов'язаний перейти за адресою `Location` без передачі заголовка `Authorization` реєстру, щоб не скомпрометувати облікові дані перед стороннім хостом.
- **Підтримка докачування (Resumable Pull):** Запит із заголовком `Range: bytes=1048576-` повертає `206 Partial Content` із заголовком `Content-Range: bytes 1048576-5242879/5242880`.

---

### 2.7. Перевірка наявності блобу (Blob Existence Check)
```http
HEAD /v2/<name>/blobs/<digest>
```
- **Призначення:** Використовується клієнтом перед завантаженням (push/pull) для дедуплікації: якщо блоб уже є в сховищі, повторне завантаження пропускається.
- **Успішна відповідь:** `200 OK`
  - `Content-Length: <size_in_bytes>`
  - `Docker-Content-Digest: sha256:...`
- **Помилка відсутності:** `404 Not Found` (`BLOB_UNKNOWN`).

---

### 2.8. Ініціалізація завантаження блобу (Blob Upload Initiation)
```http
POST /v2/<name>/blobs/uploads/
```
- **Варіант 1 (Двоетапне сесійне завантаження):** Запит без додаткових параметрів.
  - Відповідь: `202 Accepted`
  - `Location: /v2/<name>/blobs/uploads/<session_uuid>`
  - `Range: bytes=0-0`
  - `Docker-Upload-UUID: <session_uuid>`
- **Варіант 2 (Однопрохідне монолітне завантаження):**
  - `POST /v2/<name>/blobs/uploads/?digest=sha256:<digest>`
  - `Content-Length: <size>`
  - Тіло запиту: весь потік байтів блобу.
  - Відповідь: `201 Created` (`Location: /v2/<name>/blobs/sha256:<digest>`).
- **Варіант 3 (Міжрепозиторійне монтування — Cross-Repository Blob Mount):**
  - `POST /v2/<name>/blobs/uploads/?mount=sha256:<digest>&from=<source_repository>`
  - Якщо користувач має права на читання репозиторію `<source_repository>` і вказаний блоб там існує, реєстр миттєво прив'язує блоб до нового репозиторію без передачі даних по мережі.
  - Відповідь при успіху монтування: `201 Created` (`Location: /v2/<name>/blobs/sha256:<digest>`).
  - Відповідь при відсутності блобу в джерелі: `202 Accepted` (реєстр повертає звичайну сесію для фізичного завантаження).

---

### 2.9. Потокова передача частин блобу (Chunked Upload)
```http
PATCH /v2/<name>/blobs/uploads/<session_uuid>
```
- **Заголовки запиту:**
  - `Content-Type: application/octet-stream`
  - `Content-Range: <start_byte>-<end_byte>`
  - `Content-Length: <chunk_size>`
- **Тіло:** бінарний зріз даних.
- **Відповідь:** `202 Accepted`
  - `Location: /v2/<name>/blobs/uploads/<session_uuid>`
  - `Range: bytes=0-<last_uploaded_byte>`

---

### 2.10. Фіналізація завантаження блобу
```http
PUT /v2/<name>/blobs/uploads/<session_uuid>?digest=sha256:<digest>
```
- **Призначення:** Атомарна перевірка отриманих байтів проти очікуваного SHA-256 хешу та перенесення блобу в постійний пул CAS.
- **Успішна відповідь:** `201 Created`
  - `Location: /v2/<name>/blobs/sha256:<digest>`
  - `Docker-Content-Digest: sha256:<digest>`

---

### 2.11. Отримання списку тегів репозиторію (Tag Listing)
```http
GET /v2/<name>/tags/list?n=<limit>&last=<last_tag>
```
- **Параметри запиту:**
  - `n` — кількість тегів на сторінку (пагінація).
  - `last` — останній отриманий тег попередньої сторінки для курсорної навігації.
- **Успішна відповідь:** `200 OK`
```json
{
  "name": "myorg/backend",
  "tags": ["v1.0.0", "v1.1.0", "v1.2.0", "latest"]
}
```
- **Заголовки відповіді:**
  - `Link: </v2/myorg/backend/tags/list?n=100&last=v1.2.0>; rel="next"` (за стандартом RFC 5988).

---

### 2.12. Пошук пов'язаних артефактів (OCI 1.1 Referrers API)
```http
GET /v2/<name>/referrers/<digest>?artifactType=<type>
```
- **Призначення:** Пошук артефактів, які посилаються на конкретний образ через поле `subject` (електронні підписи Cosign, паспорти компонентів SBOM, звіти безпеки Trivy).
- **Успішна відповідь:** `200 OK`
```json
{
  "schemaVersion": 2,
  "mediaType": "application/vnd.oci.image.index.v1+json",
  "manifests": [
    {
      "mediaType": "application/vnd.oci.image.manifest.v1+json",
      "artifactType": "application/vnd.dev.cosign.simplesigning.v1+json",
      "digest": "sha256:5b7194...",
      "size": 650
    }
  ]
}
```

---

## 3. Схема стандартизованих помилок OCI

У разі збою реєстр зобов'язаний повернути відповідний HTTP-статус (`4xx` або `5xx`) та структуроване JSON-тіло:

```json
{
  "errors": [
    {
      "code": "MANIFEST_UNKNOWN",
      "message": "manifest blob unknown to registry",
      "detail": { "Tag": "v9.9.9" }
    }
  ]
}
```

### Реєстр кодів помилок (OCI Error Codes):
- `BLOB_UNKNOWN`: Вказаний криптографічний блоб відсутній у реєстрі.
- `BLOB_UPLOAD_INVALID`: Помилка стану сесії завантаження (некоректний діапазон `Content-Range`).
- `BLOB_UPLOAD_UNKNOWN`: Сесія завантаження за вказаним UUID застаріла або не існує.
- `DIGEST_INVALID`: Обчислений реєстром хеш SHA-256 не збігається з переданим параметром `?digest=`.
- `MANIFEST_BLOB_UNKNOWN`: Маніфест валідний, але один або кілька дескрипторів шарів відсутні у сховищі блобів.
- `MANIFEST_INVALID`: Синтаксична помилка валідації маніфесту за схемою JSON.
- `MANIFEST_UNKNOWN`: Маніфест за вказаним тегом або дайджестом не знайдено.
- `NAME_INVALID`: Неприпустимий формат імені репозиторію (порушення правил іменування `[a-z0-9]+([._-][a-z0-9]+)*`).
- `NAME_UNKNOWN`: Вказане ім'я репозиторію відсутнє в реєстрі.
- `SIZE_INVALID`: Розмір завантаженого блобу не збігається із заявленим у заголовку `Content-Length`.
- `TAG_INVALID`: Неприпустимий формат назви тегу (максимум 128 символів `[a-zA-Z0-9_][a-zA-Z0-9._-]*`).
- `UNAUTHORIZED`: Відсутній заголовок авторизації або наданий токен протермінований.
- `DENIED`: Доступ до операції заборонено політиками безпеки або правами доступу користувача.
- `UNSUPPORTED`: Операція не підтримується даною реалізацією реєстру.
- `TOOMANYREQUESTS`: Перевищено ліміт запитів (Rate Limit); реєстр повертає заголовок `Retry-After: <seconds>`.
