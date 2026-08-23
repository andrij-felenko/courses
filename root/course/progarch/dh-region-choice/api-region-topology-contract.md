# Декларативна специфікація топології регіонів та інтерфейси евакуації DH

Ця вставка містить довідкову специфікацію програмних інтерфейсів, декларативних контрактів конфігурації топології, REST/gRPC методів примусової ізоляції (Fencing Protocol) та схем авторизаційних токенів маршрутизації платформи Digital Homes.

Декларативний підхід до опису топології дозволяє інфраструктурній команді використовувати підходи GitOps (за допомогою ArgoCD чи Flux) для автоматичного розгортання та керування конфігурацією регіональних дата-центрів по всьому світу. При внесенні змін до репозиторію інфраструктурного коду GitOps-оператор автоматично валідує декларативну схему, перевіряє сумісність версій епохи та виконує плавну ротацію конфігураційних файлів на проксі-шлюзах без перезапуску сервісів.

У цьому документі формалізовано всі зовні описувані структури даних, правила їх валідації, коди відповідей та протоколи безпеки.

## 1. Схема конфігураційного маніфесту топології (DHRegionTopologySpec)

Декларативний конфігураційний файл `region-topology.yaml` виступає як єдине джерело правди (Single Source of Truth) для центрального оркестратора інфраструктури та мережевих шлюзів Edge PoP. Він визначає список активних регіонів, їхні максимальні ліміти ємності, параметри слотів міжрегіональної реплікації та пороги спрацьовування автоматів автоматичної евакуації.

```yaml
apiVersion: dh.digitalhomes.io/v1alpha1
kind: DHRegionTopologySpec
metadata:
  name: planet-dh-global-topology
  clusterId: dh-prod-cluster-01
  updatedAt: "2026-08-18T04:15:00Z"
spec:
  globalDirectory:
    consensusType: Raft
    quorumNodes:
      - id: node-eu-central
        region: eu-central-1
        endpoint: "gdir-eu.digitalhomes.io:9090"
      - id: node-us-east
        region: us-east-1
        endpoint: "gdir-us.digitalhomes.io:9090"
      - id: node-ap-east
        region: ap-east-1
        endpoint: "gdir-ap.digitalhomes.io:9090"
  regions:
    - name: eu-central-1
      role: Primary
      stampsCount: 12
      maxCapacityHomes: 600000
      status: Active
      fencingEpoch: 104
      replicationTarget: us-east-1
      replicationSlot: dr_us_east_1_slot
      maxReplicationLagBytes: 68719476736 # 64 GB
    - name: us-east-1
      role: WarmStandby
      stampsCount: 8
      maxCapacityHomes: 400000
      status: Active
      fencingEpoch: 104
      replicationTarget: eu-central-1
      replicationSlot: dr_eu_central_1_slot
      maxReplicationLagBytes: 68719476736 # 64 GB
    - name: ap-east-1
      role: Active
      stampsCount: 4
      maxCapacityHomes: 200000
      status: Active
      fencingEpoch: 104
      replicationTarget: us-east-1
      replicationSlot: dr_ap_us_slot
      maxReplicationLagBytes: 34359738368 # 32 GB
  failoverPolicy:
    healthCheckIntervalSeconds: 5
    consecutiveFailuresThreshold: 3
    autoEvacuationEnabled: true
    fencingTimeoutSeconds: 10
    maxAcceptableLagSeconds: 2.5
```

### Детальний опис семантики полів специфікації

- `spec.globalDirectory.consensusType`: Модель консенсусу глобального реєстру (значення `Raft` або `Paxos`). Визначає правила формування більшості при виконанні міжрегіональних транзакцій.
- `spec.regions[].role`: Функціональна роль дата-центру. Можливі значення: `Primary` (основний регіон прийому записів для закріплених будинків), `WarmStandby` (гарячий резерв із прийманням асинхронних WAL-логів), `Active` (автономний активний регіон для власної групи будинків).
- `spec.regions[].stampsCount`: Кількість ізольованих штампів (Stamps) усередині дата-центру. Кожен штамп розрахований на обслуговування до 50 000 домашніх хабів для локалізації радіусу вибуху (Blast Radius).
- `spec.regions[].fencingEpoch`: Глобальний монотонно зростаючий лічильник епохи ізоляції. При кожній аварійній евакуації значення інкрементується на одиницю. Будь-який запит із `fencingEpoch` меншим за поточне значення на сервері відхиляється шлюзом.
- `spec.regions[].maxReplicationLagBytes`: Максимально припустимий розмір накопичених невичитаних логів WAL (у байтах) у слоті реплікації PostgreSQL. При перевищенні цього ліміту слот тимчасово інвалідується для захисту дискового простору первинного дата-центру.
- `spec.failoverPolicy.maxAcceptableLagSeconds`: Гранично припустимий часовий лаг реплікації RPO у секундах, за якого автоматичному контролеру дозволено виконувати перемикання ролей на резервний DC у режимі `Full Active`.

## 2. API примусової ізоляції дата-центру (Fencing Protocol REST API)

Під час виконання аварійної евакуації деградованого дата-центру автоматичний евакуаційний контролер (Evacuation Controller) надсилає серію захищених команд до Fencing API ізольованого та резервного регіонів.

Головна мета Fencing API — гарантувати припинення будь-яких операцій запису у пошкодженому дата-центрі до того, як резервний дата-центр почне приймати новий трафік, що повністю виключає виникнення Split-Brain. При виклику API контролер використовує тайм-аут у 10 секунд; якщо пошкоджений DC не відповідає на виклик ізоляції, контролер застосовує мережеве фенсингування на рівні BGP-маршрутизаторів та eBPF-фільтрів.

### Endpoint: POST /api/v1/fencing/isolate

Надсилає команду негайного переходу дата-центру в стан примусової ізоляції (Fenced State).

**Заголовки запиту:**
- `Authorization: Bearer <FencingAdminJWTToken>` — криптографічний JWT-токен із правами кластерного адміністратора.
- `Content-Type: application/json`
- `X-DH-Fencing-Epoch: 105` — нова епоха ізоляції.

**Тіло запиту:**
```json
{
  "targetRegion": "eu-central-1",
  "newFencingEpoch": 105,
  "reason": "Asymmetric network partition detected by Deep Health Gate",
  "action": "REVOKE_WRITE_KEYS_AND_FLUSH_INGRESS",
  "initiatedBy": "evacuation-controller-us-east-01"
}
```

**Відповідь у разі успіху (HTTP 200 OK):**
```json
{
  "status": "SUCCESS",
  "region": "eu-central-1",
  "appliedEpoch": 105,
  "ingressRulesFlushed": true,
  "activeConnectionsTerminated": 412850,
  "walSenderTerminated": true,
  "timestamp": "2026-08-18T04:15:12.450Z"
}
```

**Відповідь при помилці конфлікту епохи (HTTP 409 Conflict):**
```json
{
  "errorCode": "FENCING_EPOCH_STALE",
  "message": "Current region epoch (106) is higher than requested epoch (105)",
  "currentEpoch": 106,
  "timestamp": "2026-08-18T04:15:12.480Z"
}
```

### Endpoint: POST /api/v1/fencing/promote

Надсилає команду активації ролі первинного дата-центру та зняття обмежень запису у резервному регіоні.

**Тіло запиту:**
```json
{
  "targetRegion": "us-east-1",
  "expectedFencingEpoch": 105,
  "mode": "PROMOTE_TO_FULL_ACTIVE",
  "verifyLagZero": true
}
```

**Відповідь при успішній активації (HTTP 200 OK):**
```json
{
  "status": "PROMOTED",
  "region": "us-east-1",
  "fencingEpoch": 105,
  "readOnlyModeDisabled": true,
  "promotedAt": "2026-08-18T04:15:15.110Z"
}
```

## 3. Схема токена маршрутизації та Fencing Epoch (DH-Routing-Token)

Для забезпечення безпеки та миттєвої валідації маршрутів на краю мережі кожен клієнтський запит від хаба передає шифрований заголовок `X-DH-Routing-Token`. Токен підписується криптографічним ключем HMAC-SHA256 або RSA-2048 і містить метадані закріплення будинку.

Використання компактних токенів з HMAC-підписом дозволяє геомаршрутизатору перевіряти автентичність запиту без звернення до бази даних IAM, що знижує навантаження на процесори шлюзів та усуває додаткові мережеві затримки.

Структура розпакованого JSON-об'єкта токена:

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
.
{
  "sub": "home_8841",
  "primaryRegion": "eu-central-1",
  "failoverRegion": "us-east-1",
  "stampId": "stamp-04",
  "fencingEpoch": 104,
  "dataResidencyLocked": true,
  "iat": 1786940100,
  "exp": 1786943700
}
.
[HMAC-SHA256 Signature]
```

### Валідація токена на edge-шлюзі
При отриманні токена георутер перевіряє:
1. Валідність підпису HMAC за допомогою локального публічного ключа.
2. Термін придатності токена (`exp > now`).
3. Значення `fencingEpoch`: якщо значення в токені менше за поточне значення у кші шлюзу, токен вважається анульованим, і клієнт перенаправляється на повторну авторизацію.

## 4. Специфікація Deep Health Check API

Сервіс моніторингу стану доступності дата-центру надає розширений HTTP/gRPC endpoint `/health/deep`, який використовується автоматичними контролерами для відстеження стану локальних компонентів.

Глибока перевірка стану виконується кожні 5 секунд. На відміну від звичайного ping-запиту, Deep Health Check ініціює реальну тестову транзакцію запису у тимчасову таблицю локального PostgreSQL та перевіряє доступний обсяг вільного дискового простору.

### Endpoint: GET /health/deep

Перевіряє доступність локальної бази даних PostgreSQL, статус фізичного дискового масиву NVMe, стан слота реплікації та зв'язок з Global Directory.

**Приклад успішної відповіді (HTTP 200 OK):**
```json
{
  "status": "HEALTHY",
  "region": "eu-central-1",
  "components": {
    "database": {
      "status": "UP",
      "writable": true,
      "connectionPoolActive": 42,
      "diskSpaceFreePercent": 68.5
    },
    "replicationSlot": {
      "status": "UP",
      "slotName": "dr_us_east_1_slot",
      "lagBytes": 1048576,
      "lagSeconds": 0.12
    },
    "globalDirectorySync": {
      "status": "UP",
      "raftState": "Leader",
      "lastHeartbeatMs": 12
    }
  }
}
```

**Приклад відповіді при деградації (HTTP 503 Service Unavailable):**
```json
{
  "status": "DEGRADED",
  "region": "eu-central-1",
  "components": {
    "database": {
      "status": "READ_ONLY",
      "writable": false,
      "reason": "NVMe array read-only lockout triggered by I/O error"
    },
    "replicationSlot": {
      "status": "DISCONNECTED",
      "lagBytes": 52428800
    }
  }
}
```

## 5. Повний довідник кодів помилок та матриця інспегування

У цій таблиці наведено вичерпний перелік системних кодів помилок, які повертаються API-інтерфейсами евакуації та маршрутизації платформи Digital Homes, а також порядок дій для клієнтських систем.

| Код помилки | HTTP Статус | Причина виникнення | Автоматична реакція клієнта / Edge Proxy |
| :--- | :--- | :--- | :--- |
| `FENCING_EPOCH_STALE` | 409 Conflict | Запит містить застарілу епоху фенсингу. Регіон було ізольовано від записів. | Скинути локальний кш маршрутів, виконати запит оновленого токена у Global Directory. |
| `REGION_READ_ONLY` | 503 Temp | Регіон перебуває у фазі Catch-up і приймає лише операції читання. | Повторити спробу запису з експоненційним відступом та джиттером через 2...5 секунд. |
| `STAMP_CAPACITY_EXCEEDED` | 507 Insufficient | Локальний штамп досяг ліміту 50 000 будинків. | Перенаправити запит створення нового будинку на сусідній штамп у межах регіону. |
| `DATA_RESIDENCY_VIOLATION` | 403 Forbidden | Спроба евакуації будинку з прапором Lock у неприпустимий дата-центр. | Заблокувати евакуацію, сформувати сповіщення для чергової зміни SRE. |
| `REPLICATION_LAG_TOO_HIGH` | 412 Precondition | Лаг реплікації резервного DC перевищує ліміт `maxAcceptableLagSeconds`. | Відхилити автоматичний Promote, перевести евакуацію в режим ручного підтвердження. |
| `TOKEN_SIGNATURE_INVALID` | 401 Unauthorized | Підпис токена маршрутизації не пройшов перевірку ключем HMAC. | Відхилити з'єднання, вимагати повторного проходження mTLS-авторизації. |

## 6. Протокол безпеки та ротація ключів автентифікації

Усі виклики Fencing API між дата-центрами вимагають суворого дотримання взаємної автентифікації mTLS із використанням криптографічних сертифікатів x509v3.

Ключі підпису токенів `DH-Routing-Token` ротуються автоматично кожні 24 години за допомогою сервісу HashiCorp Vault. Під час ротації шлюзи зберігають попередній публічний ключ протягом 48 годин для забезпечення плавної ротації токенів без збоїв у активних клієнтських сесіях. Якщо спроба ротації ключів зазнає невдачі через міжрегіональний обрив мережі, локальний кеш ключів продовжує функціонувати в автономному режимі до відновлення зв'язку з Vault.
