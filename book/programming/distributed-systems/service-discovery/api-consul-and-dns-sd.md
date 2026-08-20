# 📋 Протоколи та контракти: Consul HTTP API, DNS-SD (RFC 2782) та Kubernetes EndpointSlice

Щоб розподілена система могла динамічно керувати маршрутизацією, компоненти взаємодіють через чітко стандартизовані мережеві протоколи та формати даних. Незалежно від мови програмування чи платформи оркестрації, протокол виявлення сервісів визначає три базові операції: **реєстрацію екземпляра (Registration)**, **підтвердження працездатності (Heartbeat / Health Check)** та **отримання актуального каталогу (Discovery Query / Watch)**.

Розгляньмо детальні специфікації, структуру полів, бінарні та текстові формати чотирьох фундаментальних контрактів індустрії.

## 1. HashiCorp Consul Agent та Catalog HTTP API

У системі Consul існує важливе архітектурне розмежування між **Agent API** (локальний демон на хості) та **Catalog API** (централізоване сховище кластера).

### 1.1. Реєстрація сервісу через Agent API

Для додавання екземпляра до каталогу застосунок (або допоміжний скрипт ініціалізації) надсилає `PUT`-запит до локального агента Consul на порт 8500:

```http
PUT /v1/agent/service/register HTTP/1.1
Host: 127.0.0.1:8500
Content-Type: application/json
X-Consul-Token: b9f482a1-6312-4c89-9a22-421b8f1023a1
```

```json
{
  "ID": "payment-srv-node04-8080",
  "Name": "payment-service",
  "Tags": ["v1.4.2", "production", "zone-eu-west-1a"],
  "Address": "10.0.4.19",
  "Port": 8080,
  "Meta": {
    "protocol": "http/2",
    "git_sha": "a4f891b",
    "weight": "100",
    "az": "eu-west-1a"
  },
  "EnableTagOverride": false,
  "Check": {
    "CheckID": "payment-srv-ttl-check",
    "Name": "Payment Service Heartbeat TTL",
    "Notes": "HTTP heartbeat from application background worker",
    "TTL": "10s",
    "DeregisterCriticalServiceAfter": "1m"
  },
  "Weights": {
    "Passing": 10,
    "Warning": 1
  }
}
```

#### Повний розбір структури полів:
* `ID` (рядок, обов'язковий): Унікальний первинний ключ екземпляра в межах усього кластера. Якщо зареєструвати інший сервіс із таким самим `ID`, він перезапише попередній запис.
* `Name` (рядок, обов'язковий): Логічне ім'я пулу сервісів. За цим ім'ям клієнти запитують адреси через DNS або HTTP.
* `Tags` (масив рядків): Список символічних міток для базової фільтрації (версії, типи оточення).
* `Address` (рядок): Мережева IP-адреса або хостнейм, доступний для інших вузлів кластера. Якщо поле порожнє, Consul автоматично підставляє IP-адресу хоста агента.
* `Port` (ціле число, 1–65535): Мережевий порт, на якому процес слухає вхідні з'єднання.
* `Meta` (асоціативний масив рядків): Довільні структуровані метадані для тонкого клієнтського балансування (наприклад, вага інстанса, підтримка gRPC, криптографічні хеші).
* `Check` (об'єкт): Специфікація перевірки здоров'я:
  * `TTL`: Інтервал дії оренди. Якщо застосунок не надішле оновлення протягом 10 секунд, агент переводить сервіс у стан `CRITICAL`.
  * `DeregisterCriticalServiceAfter`: Захист від засмічення реєстру. Якщо сервіс перебуває в критичному стані довше 1 хвилини, агент безумовно видаляє його запис із пам'яті.
* `Weights` (об'єкт): Вагові коефіцієнти для балансування через DNS SRV: вага при повному здоров'ї (`Passing`) та вага при деградації (`Warning`).

---

### 1.2. Протокол поновлення оренди (Heartbeat / TTL Pass)

Застосунок запускає фоновий потік, який із періодичністю `TTL / 3` (кожні 3.3 секунди для десятисекундного TTL) робить HTTP-виклик:

```http
PUT /v1/agent/check/pass/payment-srv-ttl-check HTTP/1.1
Host: 127.0.0.1:8500
Content-Type: application/json

{
  "Note": "Service healthy: memory 42%, DB connections 18/50, latency p99 12ms"
}
```

#### Можливі статуси перевірок:
1. `pass` (`PUT /v1/agent/check/pass/<id>`): Сервіс повністю працездатний.
2. `warn` (`PUT /v1/agent/check/warn/<id>`): Сервіс деградував (наприклад, пул з'єднань заповнений на 90%), але здатний обробляти частину трафіку зі зниженою вагою.
3. `fail` (`PUT /v1/agent/check/fail/<id>`): Сервіс несправний, негайно виключається з маршрутизації.

---

### 1.3. Блокуючі запити на виявлення (Consul Blocking Queries)

Для усунення постійного опитування клієнтський SDK використовує блокуючі запити над ендпоінтом `/v1/health/service`:

```http
GET /v1/health/service/payment-service?passing=true&index=18942&wait=30s&stale HTTP/1.1
Host: 127.0.0.1:8500
```

#### Параметри запиту:
* `passing=true`: Повертати виключно ті екземпляри, всі перевірки здоров'я яких мають статус `passing`.
* `index=18942`: Індекс останньої ревізії стану кластера, збережений у локальному клієнтському кеші.
* `wait=30s`: Максимальний час утримання TCP-з'єднання сервером, якщо змін не відбулося.
* `stale`: Режим читання, що дозволяє будь-якому follower-вузлу кластера відповісти з локальної репліки без звернення до Raft-лідера. Це знижує затримку відповіді до менш ніж 1 мілісекунди.

#### Спеціальні діагностичні заголовки відповіді Consul:
```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Consul-Index: 18943
X-Consul-KnownLeader: true
X-Consul-LastContact: 0
X-Consul-Effective-Consistency: stale
```
* `X-Consul-Index`: Новий монотонно зростаючий індекс версії. Клієнт зберігає його для наступного блокуючого запиту.
* `X-Consul-KnownLeader`: Булевий прапорець. Якщо `false`, кластер втратив кворум лідера Raft.
* `X-Consul-LastContact`: Час у мілісекундах від останнього контакту вузла з лідером. Дозволяє клієнту оцінити свіжість репліки.

---

## 2. Стандарт DNS-SD та формат записів SRV (RFC 2782)

Стандарт RFC 2782 визначає спосіб використання системи доменних імен для виявлення сервісів з урахуванням динамічних портів, пріоритетів та ваг.

### 2.1. Формат запису SRV у файлі зони

```dns
;; Шаблон:
;; _Service._Proto.Name. TTL Class SRV Priority Weight Port Target.

_http._tcp.payment-service.service.consul. 5 IN SRV 10 60 8080 srv1.node.dc1.consul.
_http._tcp.payment-service.service.consul. 5 IN SRV 10 40 8080 srv2.node.dc1.consul.
_http._tcp.payment-service.service.consul. 5 IN SRV 20 100 9090 backup.node.dc1.consul.
```

### 2.2. Покроковий алгоритм обробки записів клієнтом (RFC 2782)

Коли клієнт отримує масив SRV-записів, він зобов'язаний виконати таку послідовність кроків:
1. **Групування за пріоритетом (`Priority`):** Клієнт обирає записи з найменшим числовим значенням поля `Priority` (у нашому прикладі `Priority = 10`). Записи з більшим пріоритетом (`Priority = 20`) зберігаються як резервні (failover) і використовуються лише тоді, коли всі хости з першої групи виявляться недоступними.
2. **Зважений випадковий вибір за вагою (`Weight`):** Якщо у вибраній групі є кілька записів, клієнт обчислює суму ваг `Sum = W1 + W2 + ... + Wn`. Потім генерується випадкове число `R` у діапазоні `[0, Sum)`. Клієнт ітерує по записах, накопичуючи вагу, і обирає той хост, на якому накопичена сума перевищує `R`.
3. **Вилучення порту (`Port`):** Клієнт використовує поле `Port` для відкриття TCP-сокету до отриманого `Target`.

### 2.3. Додаткова секція DNS (Additional Records) та прапорець урізання TC

Щоб уникнути подвійного мережевого RTT (один запит на SRV, другий на A-запис цільового імені), сервер повертає IP-адреси в секції `ADDITIONAL`:

```dns
;; QUESTION SECTION:
;_http._tcp.payment-service.service.consul. IN SRV

;; ANSWER SECTION:
_http._tcp.payment-service.service.consul. 5 IN SRV 10 60 8080 srv1.node.dc1.consul.
_http._tcp.payment-service.service.consul. 5 IN SRV 10 40 8080 srv2.node.dc1.consul.

;; ADDITIONAL SECTION:
srv1.node.dc1.consul. 5 IN A 10.0.4.19
srv2.node.dc1.consul. 5 IN A 10.0.4.22
```

Якщо розмір DNS-відповіді через UDP перевищує 512 байтів (або погоджений розмір буфера EDNS0 4096 байтів), сервер виставляє прапорець **Truncated (TC = 1)** у заголовку DNS. Отримавши такий прапорець, клієнт зобов'язаний негайно перемкнутися на протокол TCP на порту 53 і повторити запит для завантаження повного пакету.

---

## 3. Специфікація Kubernetes EndpointSlice API (`discovery.k8s.io/v1`)

У сучасних версіях Kubernetes контролер `EndpointSlice` замінив застарілий об'єкт `Endpoints`, вирішивши проблему квадратичного зростання навантаження на сховище `etcd` при масштабуванні кластерів.

```yaml
apiVersion: discovery.k8s.io/v1
kind: EndpointSlice
metadata:
  name: payment-service-ab78k
  namespace: production
  labels:
    kubernetes.io/service-name: payment-service
    endpointslice.kubernetes.io/managed-by: endpointslice-controller.k8s.io
addressType: IPv4
ports:
  - name: http-api
    protocol: TCP
    port: 8080
    appProtocol: http
  - name: metrics
    protocol: TCP
    port: 9102
    appProtocol: prometheus
endpoints:
  - addresses:
      - "10.244.2.15"
    conditions:
      ready: true
      serving: true
      terminating: false
    nodeName: "k8s-worker-node-02"
    zone: "eu-west-1a"
    hints:
      forZones:
        - name: "eu-west-1a"
    targetRef:
      kind: Pod
      namespace: production
      name: payment-deployment-7d9b9-xf42a
      uid: "5c71b693-41a2-4a0b-9df0-9bfa08123abc"
      resourceVersion: "4920194"
  - addresses:
      - "10.244.3.44"
    conditions:
      ready: false
      serving: true
      terminating: true
    nodeName: "k8s-worker-node-03"
    zone: "eu-west-1b"
    targetRef:
      kind: Pod
      namespace: production
      name: payment-deployment-7d9b9-mk89p
      uid: "7e9124a1-89b1-411f-8aa3-11bb09923def"
```

### 3.1. Детальний аналіз прапорців `conditions`:
* `ready: true`: Контейнер успішно пройшов усі проби готовності (Readiness Probes) і готовий приймати нові клієнтські запити.
* `serving: true`: Под зараз здатний обробляти трафік. Зверніть увагу на другий ендпоінт у прикладі: под отримав сигнал `SIGTERM` і перебуває в стані видалення (`terminating: true`, `ready: false`), проте він продовжує обробляти вже відкриті транзакції (`serving: true`), поки не спливе таймер `terminationGracePeriodSeconds`.
* `terminating: false`: Под працює штатно і не запланований на знищення.
* `hints.forZones`: Топологічні підказки (Topology Aware Hints). Дозволяють `kube-proxy` та Envoy маршрутизувати трафік виключно всередині тієї самої зони доступності (`eu-west-1a`), заощаджуючи затримку та вартість міжзонального трафіку.

---

## 4. Контракт Envoy Endpoint Discovery Service (xDS v3 EDS)

У сервісних сітках (Service Mesh) проксі-сайдкари оновлюють списки бекендів через бінарний потоковий gRPC-протокол **Envoy EDS**.

### 4.1. Protobuf-структура `ClusterLoadAssignment`

```protobuf
syntax = "proto3";

package envoy.config.endpoint.v3;

message ClusterLoadAssignment {
  string cluster_name = 1;
  repeated LocalityLbEndpoints endpoints = 2;
  NamedEndpointsPolicy policy = 4;
}

message LocalityLbEndpoints {
  envoy.config.core.v3.Locality locality = 1; // region, zone, sub_zone
  repeated LbEndpoint lb_endpoints = 2;
  google.protobuf.UInt32Value load_balancing_weight = 3;
  uint32 priority = 5;
}

message LbEndpoint {
  oneof host_identifier {
    Endpoint endpoint = 1;
    string endpoint_name = 2;
  }
  core.v3.HealthStatus health_status = 2;
  google.protobuf.UInt32Value load_balancing_weight = 3;
}
```

### 4.2. Механізм пріоритетів та локальності в Envoy xDS
* **Пріоритетні рівні (Priority Levels):** Envoy групує ендпоінти за числовим рівнем `priority` (0 — основний, 1 — резервний). Envoy завжди направляє 100% трафіку на рівень `P = 0`. Якщо відсоток здорових хостів на рівні 0 падає нижче порогу (наприклад, менше 50%), Envoy автоматично починає переливати частину трафіку на рівень `P = 1` за пропорційною формулою.
* **Локальність (Locality):** Кожен ендпоінт містить інформацію про свій регіон і зону. Площина управління (Istiod) конфігурує сайдкар так, щоб він надавав перевагу локальним бекендам, мінімізуючи затримку.

---

## Порівняння протоколів та контрактів виявлення

| Властивість | Consul Agent HTTP API | DNS-SD (RFC 2782 SRV) | K8s EndpointSlice | Envoy xDS v3 EDS |
| :--- | :--- | :--- | :--- | :--- |
| **Транспортний протокол** | HTTP/1.1, HTTP/2 (REST) | DNS (UDP / TCP порт 53) | HTTPS (K8s API Server) | gRPC по HTTP/2 |
| **Формат серіалізації** | JSON | Бінарний DNS Wire Format | JSON / Protocol Buffers | Protocol Buffers v3 |
| **Модель оновлень** | Long Polling (`wait=30s`) | Періодичний запит за TTL | Watch / Informer (SSE/Chunked) | Двонаправлений gRPC Stream |
| **Підтримка динамічних портів** | Повна | Повна (поле `Port`) | Повна (масив `ports`) | Повна (`SocketAddress.port`) |
| **Метадані екземпляра** | Багаті (Tags, Meta KV) | Обмежені (Priority, Weight) | Багаті (Zone, Conditions, PodRef) | Максимальні (Locality, Weight, Metadata) |
| **Затримка оновлення** | 10–50 мс | Секунди (обмежено TTL) | 50–200 мс | < 10 мс |
| **Навантаження на мережу** | Низьке (блокуюче з'єднання) | Високе при малому TTL | Низьке (дельта-зрізи) | Мінімальне (бінарний потік) |
