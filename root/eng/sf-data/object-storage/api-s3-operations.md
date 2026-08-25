# 📋 Протокол S3 REST API: структура запитів, заголовки та керування доступом

Повна специфікація протоколу S3 REST API визначає семантику HTTP-методів, структуру заголовків метаданих, параметри пагінації, контракти багаточастинного завантаження, політики безпеки, сповіщення про події, тегування та формати обробки помилок для взаємодії з об'єктними сховищами.

## Семантика адресного простору та базові операції над об'єктами

Протокол S3 базується на архітектурному стилі REST поверх стандартного транспорту HTTP/1.1 та HTTP/2. Усі ресурси організовані у двійкову ієрархію: контейнер найвищого рівня називається **бакетом (Bucket)**, а кожна окрема одиниця даних — **об'єктом (Object)**, що ідентифікується рядковим **ключем (Key)**.

Для адресації об'єктів у розподіленому кластері застосовуються дві стандартизовані моделі формування URL:

1. **Стиль віртуального хосту (Virtual-Hosted-Style Routing).** Ім'я бакета виноситься в піддомен доменного імені сховища: `https://my-bucket.s3.eu-central-1.amazonaws.com/media/video.mp4`. Усі сучасні хмарні провайдери та клієнтські SDK вимагають саме цей стиль, оскільки він дозволяє ізолювати трафік окремих бакетів на рівні маршрутизації DNS, підключати персональні сертифікати SSL/TLS та ефективно розподіляти запити між пулами вхідних проксі-серверів.
2. **Стиль шляху (Path-Style Routing).** Ім'я бакета розміщується як перший сегмент URI-шляху: `https://s3.eu-central-1.amazonaws.com/my-bucket/media/video.mp4`. Цей стиль вважається застарілим у публічних хмарах, проте широко застосовується в локальних інфраструктурах (наприклад, під час тестування проти MinIO на `localhost:9000`), де динамічне створення піддоменів у локальному DNS є ускладненим.

Операції створення, отримання, перевірки метаданих та видалення об'єктів повністю транслюються на стандартні дієслова протоколу HTTP:

| Метод | HTTP-шлях | Призначення | Тіло запиту | Тіло відповіді |
| :--- | :--- | :--- | :--- | :--- |
| `PUT` | `/{bucket}/{key}` | Створення або повний перезапис об'єкта | Двійковий потік байтів | Порожнє (ETag у заголовку) |
| `GET` | `/{bucket}/{key}` | Читання вмісту та системних метаданих | Відсутнє | Двійковий потік байтів |
| `HEAD` | `/{bucket}/{key}` | Отримання виключно метаданих без тіла | Відсутнє | Відсутнє (лише заголовки) |
| `DELETE` | `/{bucket}/{key}` | Видалення об'єкта зі сховища | Відсутнє | Порожнє (HTTP 204 No Content) |
| `POST` | `/{bucket}?delete` | Пакетне атомарне видалення до 1000 об'єктів | XML зі списком ключів | XML зі звітом про видалення |

### Механіка виконання запиту PUT Object

Операція `PUT` здійснює атомарне збереження об'єкта. Якщо об'єкт із таким ключем уже існував у бакеті, стара версія негайно замінюється новою, а всі наступні запити на читання гарантовано бачать оновлений вміст завдяки моделі суворої узгодженості (Strong Consistency).

У заголовках запиту клієнт зобов'язаний передати точний розмір у байтах (`Content-Length`), бажаний тип контенту (`Content-Type`) та за потреби клас зберігання чи криптографічний хеш MD5 для контролю цілісності на льоту:

```http
PUT /photos/2026/avatar.jpg HTTP/1.1
Host: media-bucket.s3.eu-central-1.amazonaws.com
Date: Thu, 20 Aug 2026 12:00:00 GMT
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20260820/eu-central-1/s3/aws4_request, SignedHeaders=content-length;content-type;host;x-amz-date;x-amz-storage-class, Signature=...
Content-Type: image/jpeg
Content-Length: 1048576
x-amz-storage-class: STANDARD
x-amz-meta-author: user_42
x-amz-meta-department: engineering
Content-MD5: Q2hlY2tzdW0gVmFsaWRhdGlvbg==

[... 1 048 576 двійкових байтів файлу JPEG ...]
```

Сховище обчислює хеш отриманого потоку в міру запису на накопичувачі. Якщо передано заголовок `Content-MD5`, і він не збігається з фактично збереженими байтами, сховище скасовує транзакцію, видаляє пошкоджені байти та повертає статус `400 BadDigest`.

У разі успіху повертається статус `200 OK` із заголовком `ETag` (Entity Tag), який містить шістнадцятковий MD5-хеш об'єкта у подвійних лапках:

```http
HTTP/1.1 200 OK
x-amz-id-2: LriByRT6OnhgahLq456EXAMPLE...
x-amz-request-id: 79104EXAMPLE1234
Date: Thu, 20 Aug 2026 12:00:01 GMT
ETag: "9baddb367eee81ee20ad92f77957be43"
x-amz-server-side-encryption: AES256
Content-Length: 0
```

### Механіка запитів GET та HEAD Object

Запит `GET` завантажує все тіло об'єкта та повертає всі асоційовані з ним системні й користувацькі метадані.

Запит `HEAD` виконує абсолютно аналогічну маршрутизацію та перевірку прав доступу, проте повертає виключно HTTP-заголовки з нульовим тілом відповіді. Цей метод критично важливий для високонавантажених систем: він дозволяє перевірити факт існування файлу, дізнатися його точний розмір у байтах, перевірити дату модифікації або звірити `ETag` без витрат мережевого трафіку на завантаження самого масивного блоба.

## Специфікація заголовків метаданих та системних розширень

Протокол S3 чітко розмежовує стандартні заголовки HTTP/1.1, інфраструктурні керуючі заголовки з префіксом `x-amz-*` та користувацькі атрибути з префіксом `x-amz-meta-*`.

| Заголовок | Тип | Опис та семантика |
| :--- | :--- | :--- |
| `Content-Type` | Стандартний | MIME-тип даних (наприклад, `image/webp`, `video/mp4`, `application/pdf`). Зберігається в метаданих і повертається клієнту під час `GET`. |
| `Content-Length` | Стандартний | Розмір тіла запиту в байтах. Для `PUT` запитів є обов'язковим, якщо не використовується chunked-стрімінг. |
| `ETag` | Стандартний | Для монолітних об'єктів — хеш MD5 у лапках (`"9baddb..."`). Для багаточастинних об'єктів — складений хеш із кількістю частин (`"d41d8c...-4"`). |
| `Content-MD5` | Стандартний | Base64-кодований 128-бітний дайджест MD5 тіла. Сховище звіряє його перед збереженням; у разі розбіжності повертається `400 BadDigest`. |
| `x-amz-storage-class` | Системний | Клас зберігання: `STANDARD`, `INTELLIGENT_TIERING`, `STANDARD_IA` (Infrequent Access), `GLACIER_IR` (Instant Retrieval), `GLACIER`, `DEEP_ARCHIVE`. |
| `x-amz-server-side-encryption` | Системний | Механізм шифрування на стороні сервера: `AES256` (ключі S3) або `aws:kms` (ключі AWS KMS). |
| `x-amz-copy-source` | Системний | Використовується в методі `PUT` для копіювання існуючого об'єкта всередині сховища без завантаження байтів через клієнта: `/{source-bucket}/{source-key}`. |
| `x-amz-meta-{name}` | Користувацький | Довільні метадані ключ-значення, прив'язані до об'єкта. Ключі автоматично переводяться в нижній регістр. Максимальний сумарний розмір метаданих — 2 КБ. |

Користувацькі метадані (`x-amz-meta-*`) є незмінними разом з об'єктом. Якщо виникає потреба оновити значення метаданих (наприклад, змінити статус модерації `x-amz-meta-status: approved`), протокол S3 не дозволяє оновити окреме поле: клієнт зобов'язаний виконати операцію копіювання об'єкта самого на себе за допомогою заголовка `x-amz-copy-source: /my-bucket/photo.jpg` та прапорця `x-amz-metadata-directive: REPLACE`.

## Умовні запити та оптимістичне блокування (Conditional Operations)

У розподілених системах кілька мікросервісів або фонових воркерів можуть одночасно намагатися оновити той самий об'єкт. Без належної координації виникає стан гонитви, коли пізніший запит перезаписує результат ранішого без відома системи (проблема Lost Update).

Щоби забезпечити оптимістичне блокування та керування паралелізмом, протокол S3 підтримує умовні HTTP-заголовки перевірки валідації:

| Заголовок | Умова спрацьовування | Статус при невиконанні |
| :--- | :--- | :--- |
| `If-Match` | Операція виконується лише якщо поточний `ETag` об'єкта точно збігається із зазначеним значенням. Запобігає перезапису файлу іншим воркером. | `412 Precondition Failed` |
| `If-None-Match` | Операція виконується, якщо об'єкт відсутній або його `ETag` відрізняється. При передачі `If-None-Match: *` для `PUT` запит створить файл лише за умови, що його ще не існує. | `412 Precondition Failed` (або `304 Not Modified` для `GET`) |
| `If-Modified-Since` | Об'єкт повертається лише якщо він був змінений після вказаної дати UTC. Використовується клієнтами для HTTP-кешування. | `304 Not Modified` |
| `If-Unmodified-Since` | Операція виконується лише якщо об'єкт не зазнавав змін після вказаної дати. | `412 Precondition Failed` |

### Сценарій безпечного оновлення файлу конфігурації

1. Воркер читає файл `config.json` методом `GET` та зберігає отриманий заголовок `ETag: "v1_hash"`.
2. Воркер вносить зміни в локальну копію документа.
3. Воркер надсилає оновлений файл методом `PUT` із заголовком `If-Match: "v1_hash"`.
4. Якщо за цей час інший воркер уже встиг перезаписати конфігурацію (новий `ETag` став `"v2_hash"`), сховище атомарно відхиляє запит зі статусом `412 Precondition Failed`. Воркер відловлює помилку, заново вичитує свіжий стан і повторює бізнес-логіку.

## Лістинг об'єктів та емуляція каталогів (ListObjectsV2)

Оскільки простір імен об'єктного сховища є абсолютно пласким, операція перегляду вмісту спирається на сканування відсортованого за алфавітом індексу ключів. Сучасний стандарт API використовує метод `GET /{bucket}?list-type=2`.

### Параметри фільтрації та керування вибіркою

| Параметр | Тип | Опис та правила використання |
| :--- | :--- | :--- |
| `list-type` | Ціле число | Обов'язкове значення `2` для використання сучасної оптимізованої версії API. |
| `prefix` | Рядок | Обмежує вибірку ключами, що починаються з вказаного префікса (наприклад, `users/42/`). Працює як швидкий пошук за початком рядка в B-дереві або LSM-дереві метаданих. |
| `delimiter` | Рядок | Символ групування (зазвичай `/`). Усі ключі між префіксом і першим входженням роздільника згортаються в елементи `<CommonPrefixes>`, емулюючи папки. |
| `max-keys` | Ціле число | Максимальна кількість ключів у відповіді (за замовчуванням 1000, максимум 1000). Захищає сховище від перевантаження пам'яті. |
| `continuation-token` | Рядок | Непрозорий маркер для отримання наступної сторінки результатів, якщо у відповіді встановлено прапорець `IsTruncated = true`. |
| `start-after` | Рядок | Почати лістинг строго після вказаного ключа (використовується для першої сторінки замість маркера пагінації). |

### XML-документ відповіді ListObjectsV2

Відповідь повертає детальну інформацію про знайдені об'єкти (розмір, дату зміни, клас зберігання, ETag) та віртуальні каталоги (`CommonPrefixes`):

```xml
HTTP/1.1 200 OK
Content-Type: application/xml

<ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
    <Name>media-bucket</Name>
    <Prefix>photos/</Prefix>
    <Delimiter>/</Delimiter>
    <MaxKeys>1000</MaxKeys>
    <IsTruncated>false</IsTruncated>
    
    <!-- Згорнуті віртуальні підкаталоги -->
    <CommonPrefixes>
        <Prefix>photos/2025/</Prefix>
    </CommonPrefixes>
    <CommonPrefixes>
        <Prefix>photos/2026/</Prefix>
    </CommonPrefixes>
    
    <!-- Об'єкти, що безпосередньо лежать у префіксі photos/ -->
    <Contents>
        <Key>photos/cover.jpg</Key>
        <LastModified>2026-08-20T11:30:00.000Z</LastModified>
        <ETag>"9baddb367eee81ee20ad92f77957be43"</ETag>
        <Size>2048500</Size>
        <StorageClass>STANDARD</StorageClass>
    </Contents>
</ListBucketResult>
```

Якщо загальна кількість об'єктів перевищує `max-keys`, поле `<IsTruncated>` отримує значення `true`, а у відповіді повертається поле `<NextContinuationToken>token_string</NextContinuationToken>`. Щоби отримати наступну порцію результатів, клієнт надсилає новий запит із параметром `continuation-token=token_string`.

## Повний протокол багаточастинного завантаження (Multipart Upload)

Багаточастинне завантаження є обов'язковим стандартом для будь-яких файлів розміром понад 100 МБ і єдиним способом завантажити об'єкти розміром до 5 ТБ (максимальний розмір одиночного `PUT` становить 5 ГБ).

Контракт складається з чотирьох послідовних фаз:

```
[Клієнт]                                                  [S3 Сховище]
   |                                                           |
   |--- 1. POST /bucket/video.mp4?uploads -------------------->| (Ініціалізація)
   |<-- 200 OK <InitiateMultipartUploadResult> (UploadId) -----|
   |                                                           |
   |--- 2. PUT /bucket/video.mp4?partNumber=1&uploadId=... --->| (Паралельне завантаження)
   |<-- 200 OK (ETag: "hash_1") -------------------------------|
   |                                                           |
   |--- 3. PUT /bucket/video.mp4?partNumber=2&uploadId=... --->|
   |<-- 200 OK (ETag: "hash_2") -------------------------------|
   |                                                           |
   |--- 4. POST /bucket/video.mp4?uploadId=... (XML Маніфест) ->| (Фіналізація)
   |<-- 200 OK <CompleteMultipartUploadResult> (Composite ETag)|
```

### Фаза 1: Ініціалізація завантаження (CreateMultipartUpload)

Клієнт повідомляє сховище про намір створити багаточастинний об'єкт. У запиті передаються всі фінальні метадані об'єкта (Content-Type, x-amz-meta-*), які будуть застосовані після збирання:

```http
POST /video.mp4?uploads HTTP/1.1
Host: media-bucket.s3.eu-central-1.amazonaws.com
Content-Type: video/mp4
x-amz-storage-class: STANDARD
```

Сховище створює запис сесії завантаження та повертає унікальний рядок `UploadId`:

```xml
<InitiateMultipartUploadResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
    <Bucket>media-bucket</Bucket>
    <Key>video.mp4</Key>
    <UploadId>VXBsb2FkIElEIGV4YW1wbGU</UploadId>
</InitiateMultipartUploadResult>
```

### Фаза 2: Завантаження незалежних частин (UploadPart)

Клієнт розбиває вихідний файл на фрагменти розміром від 5 МБ до 5 ГБ (лише остання фінальна частина може бути меншою за 5 МБ). Кожна частина завантажується окремим `PUT` запитом із зазначенням номера частини `partNumber` (від 1 до 10000) та отриманого `uploadId`:

```http
PUT /video.mp4?partNumber=1&uploadId=VXBsb2FkIElEIGV4YW1wbGU HTTP/1.1
Host: media-bucket.s3.eu-central-1.amazonaws.com
Content-Length: 10485760

[... 10 МБ двійкових даних частини 1 ...]
```

Сховище зберігає байти чанка на внутрішніх дисках і повертає заголовок `ETag: "d41d8cd98f00b204e9800998ecf8427e"`. Клієнтська програма зобов'язана акумулювати пари `(partNumber, ETag)` у локальній пам'яті. Частини можна завантажувати паралельно в довільному порядку; у разі мережевого обриву окремої частини повторюється передача лише цього одного чанка.

### Фаза 3: Фінальна збірка маніфесту (CompleteMultipartUpload)

Коли всі частини успішно передані, клієнт надсилає запит `POST` із тілом XML, яке містить повний перелік усіх номерів частин та їхніх відповідних `ETag`, відсортованих за зростанням `PartNumber`:

```http
POST /video.mp4?uploadId=VXBsb2FkIElEIGV4YW1wbGU HTTP/1.1
Host: media-bucket.s3.eu-central-1.amazonaws.com
Content-Type: application/xml

<CompleteMultipartUpload xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
    <Part>
        <PartNumber>1</PartNumber>
        <ETag>"d41d8cd98f00b204e9800998ecf8427e"</ETag>
    </Part>
    <Part>
        <PartNumber>2</PartNumber>
        <ETag>"e3c1556094b8a2e5ff4d41bf11019011"</ETag>
    </Part>
</CompleteMultipartUpload>
```

Сховище звіряє список частин, зв'язує збережені блоки в єдиний логічний об'єкт, обчислює складений ETag та атомарно робить об'єкт видимим для читання:

```xml
<CompleteMultipartUploadResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
    <Location>https://media-bucket.s3.eu-central-1.amazonaws.com/video.mp4</Location>
    <Bucket>media-bucket</Bucket>
    <Key>video.mp4</Key>
    <ETag>"a1b2c3d4e5f60718293a4b5c6d7e8f90-2"</ETag>
</CompleteMultipartUploadResult>
```

Складений ETag завжди містить дефіс та кількість частин наприкінці (наприклад, `-2`). Це дозволяє відрізнити багаточастинні об'єкти від монолітних на рівні клієнтських утиліт.

### Фаза 4: Аварійне скасування (AbortMultipartUpload)

Якщо завантаження перервано користувачем або сталося фатальне падіння, виклик `DELETE /key?uploadId=...` дає вказівку сховищу негайно видалити всі завантажені фрагменти, запобігаючи накопиченню «осиротілих» чанків.

## Часткове читання діапазонів байтів (Byte-Range Requests)

Об'єктне сховище підтримує стандартний заголовок HTTP/1.1 `Range` (RFC 9110), що дозволяє зчитувати довільні зрізи файлу без викачування всього об'єкта.

### Запит першого мегабайта відео

```http
GET /video.mp4 HTTP/1.1
Host: media-bucket.s3.eu-central-1.amazonaws.com
Range: bytes=0-1048575
```

### Відповідь сервера (HTTP 206 Partial Content)

```http
HTTP/1.1 206 Partial Content
Content-Range: bytes 0-1048575/104857600
Content-Length: 1048576
Content-Type: video/mp4
ETag: "a1b2c3d4e5f60718293a4b5c6d7e8f90-2"
Accept-Ranges: bytes

[... 1 048 576 байтів ...]
```

Цей механізм є основою роботи відеоплеєрів HLS/DASH, скачування архівів ZIP/TAR без повної декомпресії та виконання прямих SQL-запитів над форматами Parquet/ORC в аналітичних рушіях (AWS Athena, Trino, DuckDB).

## Параметри автентифікації у підписаних URL (Presigned Query Parameters)

При використанні Presigned URL параметри підпису SigV4 передаються в рядку запиту.

| Параметр | Приклад значення | Опис |
| :--- | :--- | :--- |
| `X-Amz-Algorithm` | `AWS4-HMAC-SHA256` | Фіксований алгоритм гешування та підпису. |
| `X-Amz-Credential` | `AKIA.../20260820/eu-central-1/s3/aws4_request` | Складений рядок: відкритий ключ, дата, регіон, сервіс і контекст. |
| `X-Amz-Date` | `20260820T120000Z` | Часова мітка створення підпису у форматі ISO 8601 UTC. |
| `X-Amz-Expires` | `900` | Термін дії посилання в секундах (ціле число від 1 до 604800). |
| `X-Amz-SignedHeaders` | `host` або `content-type;host` | Список HTTP-заголовків, включених до криптографічного підпису. |
| `X-Amz-Signature` | `a1b2c3d4...64_hex_digits...` | Обчислений 64-символьний шістнадцятковий HMAC-SHA256 підпис. |
| `X-Amz-Security-Token` | `IQoJb3JpZ2luX2VjE...` | Тимчасовий сесійний токен AWS STS (якщо використовуються IAM-ролі). |

## Політики бакета та керування доступом (Bucket Policies)

Керування правами доступу до бакета та його вмісту здійснюється за допомогою декларативних JSON-політик (Bucket Policies), які призначаються на рівні ресурсу бакета.

Політика складається з масиву тверджень `Statement`, кожне з яких містить чотири ключові елементи:
* `Effect`: дозвіл (`Allow`) або явна заборона (`Deny`). Явна заборона завжди має пріоритет над будь-якими дозволами.
* `Principal`: суб'єкт авторизації (користувач IAM, роль, інший акаунт або анонімний доступ `*`).
* `Action`: список дозволених або заборонених операцій API (наприклад, `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject`, `s3:ListBucket`).
* `Resource`: ARN-ідентифікатор ресурсу. Для дій над бакетом використовується `arn:aws:s3:::my-bucket`, а для дій над об'єктами — `arn:aws:s3:::my-bucket/*`.
* `Condition`: додаткові контекстні умови виконання (обмеження за IP-адресою, обов'язкова наявність TLS/HTTPS, перевірка типу контенту чи тегів).

### Приклад політики: примусове шифрування та обмеження IP

Нижче наведено приклад політики бакета, яка блокує будь-які запити, що надходять через незахищений протокол HTTP (без TLS), а також дозволяє завантаження файлів лише з довіреного діапазону корпоративної мережі:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "EnforceTLSRequestsOnly",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::my-secure-bucket",
        "arn:aws:s3:::my-secure-bucket/*"
      ],
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "false"
        }
      }
    },
    {
      "Sid": "AllowUploadsFromOfficeIPOnly",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:role/AppBackendRole"
      },
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::my-secure-bucket/uploads/*",
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": "198.51.100.0/24"
        }
      }
    }
  ]
}
```

## Конфігурація життєвого циклу (Lifecycle Rules)

Правила життєвого циклу (Lifecycle Configuration) автоматизують міграцію об'єктів між класами зберігання та їхнє планове видалення на основі віку або префікса.

Конфігурація задається у форматі XML за допомогою виклику `PUT /{bucket}?lifecycle`:

```xml
<LifecycleConfiguration>
    <Rule>
        <ID>MoveOldLogsToGlacierAndCleanup</ID>
        <Filter>
            <Prefix>logs/</Prefix>
        </Filter>
        <Status>Enabled</Status>
        
        <!-- Через 30 днів перемістити в холодний клас зберігання Standard-IA -->
        <Transition>
            <Days>30</Days>
            <StorageClass>STANDARD_IA</StorageClass>
        </Transition>
        
        <!-- Через 90 днів перемістити в архів Glacier -->
        <Transition>
            <Days>90</Days>
            <StorageClass>GLACIER</StorageClass>
        </Transition>
        
        <!-- Через 365 днів безповоротно видалити об'єкт -->
        <Expiration>
            <Days>365</Days>
        </Expiration>
        
        <!-- Автоматичне видалення кинутих частин Multipart Upload через 7 днів -->
        <AbortIncompleteMultipartUpload>
            <DaysAfterInitiation>7</DaysAfterInitiation>
        </AbortIncompleteMultipartUpload>
    </Rule>
</LifecycleConfiguration>
```

Директива `<AbortIncompleteMultipartUpload>` є життєво необхідною для будь-якого промислового бакета: вона гарантує, що клієнти, які розпочали передачу багаточастинних файлів і обірвали зв'язок без виклику `Abort`, не залишать у сховищі гігабайти прихованих блоків, за зберігання яких щомісяця виставляється рахунок.

## Сповіщення про події (S3 Event Notifications)

Для побудови реактивних подійно-орієнтованих архітектур (Event-Driven Architecture) сховище S3 надає механізм автоматичної генерації сповіщень під час виконання мутацій над об'єктами.

Конфігурація сповіщень (`PUT /{bucket}?notification`) визначає типи подій (`Events`) та цільові черги повідомлень (SQS), топіки публікації (SNS) або безсерверні функції (AWS Lambda):

* `s3:ObjectCreated:Put`: об'єкт створено монолітним `PUT`.
* `s3:ObjectCreated:CompleteMultipartUpload`: завершено багаточастинне завантаження.
* `s3:ObjectRemoved:Delete`: об'єкт видалено.
* `s3:ObjectRestore:Completed`: об'єкт успішно розпаковано з архіву Glacier.

### Структура JSON-повідомлення про подію

Коли клієнт завантажує файл через Presigned URL, S3 надсилає в чергу подій структурований JSON-документ:

```json
{
  "Records": [
    {
      "eventVersion": "2.1",
      "eventSource": "aws:s3",
      "awsRegion": "eu-central-1",
      "eventTime": "2026-08-20T12:05:00.000Z",
      "eventName": "ObjectCreated:Put",
      "s3": {
        "s3SchemaVersion": "1.0",
        "configurationId": "OnPhotoUploadRule",
        "bucket": {
          "name": "media-bucket",
          "arn": "arn:aws:s3:::media-bucket"
        },
        "object": {
          "key": "photos/2026/avatar.jpg",
          "size": 1048576,
          "eTag": "9baddb367eee81ee20ad92f77957be43",
          "sequencer": "0055AED6DCD90281E5"
        }
      }
    }
  ]
}
```

Поле `sequencer` містить шістнадцятковий рядок, який монотонно зростає при кожній зміні конкретного ключа. Бекенд-воркери використовують `sequencer` для визначення хронологічного порядку подій у разі, якщо мережеві повідомлення надійшли з черги не за порядком (Out-of-Order Delivery).

## Тегування об'єктів (Object Tagging API)

На відміну від метаданих `x-amz-meta-*`, які жорстко зафіксовані в тілі об'єкта і не можуть бути змінені без повного перезапису файлу, протокол S3 надає виділений підресурс **тегування об'єктів (Object Tagging)**.

Теги є динамічними парами ключ-значення (до 10 тегів на об'єкт), які можна додавати, змінювати або видаляти в будь-який момент за допомогою методів:
* `PUT /{bucket}/{key}?tagging`: призначення набору тегів без мутації самого блоба.
* `GET /{bucket}/{key}?tagging`: читання поточних тегів об'єкта.
* `DELETE /{bucket}/{key}?tagging`: очищення всіх призначених тегів.

### XML-документ запиту тегування

```xml
PUT /photos/2026/avatar.jpg?tagging HTTP/1.1
Host: media-bucket.s3.eu-central-1.amazonaws.com
Content-Type: application/xml

<Tagging xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
    <TagSet>
        <Tag>
            <Key>Environment</Key>
            <Value>Production</Value>
        </Tag>
        <Tag>
            <Key>RetentionPolicy</Key>
            <Value>LongTermArchive</Value>
        </Tag>
        <Tag>
            <Key>Confidentiality</Key>
            <Value>Internal</Value>
        </Tag>
    </TagSet>
</Tagging>
```

Теги об'єктів виконують три ключові архітектурні ролі:
1. **Фільтрація у правилах життєвого циклу.** Правило Lifecycle може переміщувати в архів Glacier не всі файли префікса, а лише ті, що мають тег `RetentionPolicy = LongTermArchive`.
2. **Атрибутивне керування доступом (ABAC / IAM).** Політика безпеки IAM може дозволяти користувачам доступ лише до тих файлів, значення тегу `Confidentiality` яких збігається з рівнем допуску користувача.
3. **Розподіл фінансових витрат (Cost Allocation).** Хмарні системи білінгу групують витрати на гігабайти пам'яті за тегом проекту або бізнес-підрозділу.

## Міждоменний доступ (CORS Configuration API)

Для організації безпечного прямого завантаження та скачування файлів із браузерів клієнтів бакет конфігурується правилами CORS через виклик `PUT /{bucket}?cors`.

Конфігурація задає білий список дозволених доменів, HTTP-методів та заголовків:

```xml
<CORSConfiguration>
    <CORSRule>
        <AllowedOrigin>https://app.example.com</AllowedOrigin>
        <AllowedOrigin>https://admin.example.com</AllowedOrigin>
        <AllowedMethod>GET</AllowedMethod>
        <AllowedMethod>PUT</AllowedMethod>
        <AllowedMethod>POST</AllowedMethod>
        <AllowedMethod>HEAD</AllowedMethod>
        <AllowedHeader>*</AllowedHeader>
        <ExposeHeader>ETag</ExposeHeader>
        <ExposeHeader>x-amz-request-id</ExposeHeader>
        <MaxAgeSeconds>3600</MaxAgeSeconds>
    </CORSRule>
</CORSConfiguration>
```

Коли браузер виконує запит завантаження, він спершу надсилає `OPTIONS`-запит із заголовками `Origin: https://app.example.com` та `Access-Control-Request-Method: PUT`. Сховище зіставляє ці значення з конфігурацією бакета та повертає статус `200 OK` із заголовком `Access-Control-Allow-Origin: https://app.example.com`, дозволяючи браузеру виконати основний транспортний запит.

## Режим незмінності Object Lock та юридичне утримання (WORM)

Для фінансових та медичних систем, що підпадають під суворі регуляторні вимоги (SEC Rule 17a-4, HIPAA, GDPR), S3 підтримує апаратний режим блокування об'єктів **Object Lock** за моделлю WORM (Write Once, Read Many).

Після активації блокування об'єкт не може бути видалений чи модифікований навіть суперкористувачем облікового запису root до настання зазначеної дати:

* **Режим управління (Governance Mode):** користувачі зі спеціальними дозволами IAM можуть зняти блокування достроково.
* **Режим відповідності (Compliance Mode):** блокування не може бути скасоване за жодних умов; навіть служба підтримки хмарного провайдера не має технічної можливості видалити файл.

Встановлення юридичного утримання здійснюється викликом `PUT /{bucket}/{key}?legal-hold`:

```xml
<LegalHold>
    <Status>ON</Status>
</LegalHold>
```

Поки прапорець `LegalHold` активний, будь-яка спроба виклику `DELETE` повертає статус `403 AccessDenied: ObjectUnderLegalHold`.

## Схема обробки помилок та коди відповідей

У разі виникнення помилки S3 повертає відповідний HTTP-статус та стандартизований XML-документ із кодом помилки та унікальним ідентифікатором запиту для аудиту:

```xml
HTTP/1.1 403 Forbidden
Content-Type: application/xml

<Error>
    <Code>SignatureDoesNotMatch</Code>
    <Message>The request signature we calculated does not match the signature you provided. Check your key and signing method.</Message>
    <AWSAccessKeyId>AKIAIOSFODNN7EXAMPLE</AWSAccessKeyId>
    <StringToSign>AWS4-HMAC-SHA256...</StringToSign>
    <RequestId>4444555566667777</RequestId>
    <HostId>K9b6WFrShortExampleHostId=</HostId>
</Error>
```

### Основні коди помилок протоколу S3

| HTTP Статус | Код помилки (Error Code) | Причина та спосіб усунення |
| :--- | :--- | :--- |
| `400 Bad Request` | `BadDigest` | Наданий заголовок `Content-MD5` не збігається з фактичним хешем переданого тіла. |
| `400 Bad Request` | `EntityTooSmall` | Розмір частини в Multipart Upload менший за 5 МБ (крім останньої частини). |
| `403 Forbidden` | `AccessDenied` | Обліковий запис не має прав `s3:GetObject` / `s3:PutObject` за політикою IAM або Bucket Policy. |
| `403 Forbidden` | `SignatureDoesNotMatch` | Невірний секретний ключ або розбіжність у канонікалізації заголовків/параметрів. |
| `403 Forbidden` | `RequestTimeTooSkewed` | Різниця між системним годинником клієнта та сервера перевищує 15 хвилин. |
| `404 Not Found` | `NoSuchBucket` | Зазначений бакет не існує в даному регіоні. |
| `404 Not Found` | `NoSuchKey` | Об'єкт із вказаним ключем відсутній у бакеті. |
| `409 Conflict` | `BucketNotEmpty` | Спроба видалити бакет, який містить об'єкти або незавершені частини Multipart Upload. |
| `412 Precond Failed` | `PreconditionFailed` | Не виконано умову заголовків `If-Match` або `If-Unmodified-Since`. |
| `416 Range Not Sat` | `InvalidRange` | Запитаний діапазон у заголовку `Range` виходить за межі фактичного розміру об'єкта. |
| `503 Service Unavail`| `SlowDown` | Перевищено ліміт запитів до префікса бакета (понад 3500 PUT/POST/DELETE або 5500 GET/HEAD на секунду). Потрібен експоненційний backoff. |
