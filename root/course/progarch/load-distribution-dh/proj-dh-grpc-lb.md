# ⚙️ Практика gRPC load balancing: GOAWAY, Connection Draining та Routing за home_id

У довгоживучих gRPC-системах на кшталт Digital Homes (де мільйони хабів тримають постійні TCP/HTTP/2 з'єднання) автоматичне масштабування бекенду не працює без двох обов'язкових механізмів: **ротації з'єднань через HTTP/2 `GOAWAY`** та **маршрутизації RPC-запитів за метаданими `home_id`**. У цій практичній вставці показано конфігурацію Envoy L7-проксі, детальний аналіз параметрів ротації сокетів та робочі реалізації контролю життєвого циклу gRPC-з'єднань чотирма мовами програмування.

## 1. Конфігурація Envoy L7: Ротація gRPC-з'єднань та EWMA Балансування

Коли мільйони пристроїв тримають довгоживучі підключення, Envoy виступає в ролі інтелектуального розпакувальника кадрів. Замість того щоб сприймати TCP-сокет як неділиму сутність, Envoy демультиплексує кадри HTTP/2, витягує заголовки кожного окремого gRPC-виклику й приймає рішення про маршрутизацію незалежно для кожного RPC.

Нижче наведено робочий фрагмент конфігурації Envoy (`envoy.yaml`), який вирішує два фундаментальні завдання:

Перше — `max_connection_duration`: параметр примушує Envoy надсилати кадр `GOAWAY` кожні 3600 секунд (+ випадковий jitter), змушуючи хаби прозоро перепідключатися до нових потів Ingest під час автоскейлінгу чи деплою. Без цієї настройки довгоживучі з'єднання залишаються на початкових подах до моменту їхнього падіння, зводячи нанівець еластичність Kubernetes-кластера.

Друге — `LEAST_REQUEST`: балансує окремі gRPC RPC-стрими всередині HTTP/2 з'єднання за алгоритмом EWMA (Peak EWMA), вибираючи між двома випадковими вузлами той, у якого найменша комбінація латентності та активних стримів.

```yaml
static_resources:
  listeners:
  - name: grpc_ingress_listener
    address:
      socket_address: { address: 0.0.0.0, port_value: 10000 }
    filter_chains:
    - filters:
      - name: envoy.filters.network.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
          stat_prefix: grpc_ingress
          # Ротація TCP-з'єднань для вирівнювання навантаження при автоскейлі
          common_http_protocol_options:
            max_connection_duration: 3600s    # Враховує jitter на боці проксі
            max_stream_duration: 300s
          http2_protocol_options:
            max_concurrent_streams: 100
            connection_keepalive:
              interval: 30s
              timeout: 10s
          route_config:
            name: dh_grpc_routes
            virtual_hosts:
            - name: ingest_service
              domains: ["*"]
              routes:
              # Маршрутизація за gRPC metadata за наявності x-home-id
              - match:
                  prefix: "/dh.ingest.v1.IngestService/"
                  headers:
                  - name: "x-home-id"
                    present_match: true
                route:
                  cluster: ingest_backend_cluster
                  hash_policy:
                  - header:
                      header_name: "x-home-id"
          http_filters:
          - name: envoy.filters.http.router
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router

  clusters:
  - name: ingest_backend_cluster
    type: STRICT_DNS
    lb_policy: LEAST_REQUEST             # EWMA балансування окремих RPC
    least_request_lb_config:
      choice_count: 2
    typed_extension_protocol_options:
      envoy.extensions.upstreams.http.v3.HttpProtocolOptions:
        "@type": type.googleapis.com/envoy.extensions.upstreams.http.v3.HttpProtocolOptions
        explicit_http2_config: {}
    load_assignment:
      cluster_name: ingest_backend_cluster
      endpoints:
      - lb_endpoints:
        - endpoint:
            address:
              socket_address: { address: ingest-node-1, port_value: 50051 }
        - endpoint:
            address:
              socket_address: { address: ingest-node-2, port_value: 50051 }
```

## 2. Налаштування gRPC Сервера: Max Connection Age & Draining

Для того щоб сервери Ingest самі могли м'яко виводити з'єднання перед деплоєм або вимкненням ноди, в інтерфейс gRPC-сервера закладають три ключові канали опцій:

1. `MaxConnectionAge`: Встановлює максимальну тривалість життя з'єднання до того, як сервер ініціює м'яке закриття через надсилання HTTP/2 кадру `GOAWAY`. Це запобігає застаюванню сокетів і гарантує регулярне перерозподілення підключень між новими екземплярами сервісу.

2. `MaxConnectionAgeGrace`: Задає додатковий віконний інтервал (наприклад, 30 секунд), протягом якого вже існуючі активні RPC-стрими можуть завершити свою роботу. Нові стрими на цьому сокеті відхиляються з вимогою відкрити нове з'єднання.

3. `Keepalive`: Загальний параметр перевірки життєздатності TCP-сокета. На відміну від стандарту TCP Keepalive (який відправляється ядром ОС із затримкою у 2 години), gRPC Keepalive відправляється на рівні застосунку кожні 30 секунд. Це захищає від «тихих» обривів Wi-Fi, коли роутер провайдера перепідключився й змінив стан NAT, а сервер продовжує вважати сокет відкритим і витрачати на нього системні ресурси.

Нижче наведено паралельні реалізації цих конфігурацій чотирма мовами програмування.

:::tabs
```cpp
// C++20: gRPC Server з розширеними параметрами ротації сокетів (Keepalive + GOAWAY)
#include <grpcpp/grpcpp.h>
#include <grpcpp/health_check_service_interface.h>
#include <chrono>
#include <memory>
#include <string_view>
#include <iostream>

using namespace std::chrono_literals;

class IngestServerFinalizer {
public:
    static std::unique_ptr<grpc::Server> CreateAndStart(std::string_view listen_addr) {
        grpc::ServerBuilder builder;
        builder.AddListeningPort(std::string(listen_addr), grpc::InsecureServerCredentials());

        // 1. MaxConnectionAge: Примусове надсилання GOAWAY через 1 годину (3600000 мс)
        builder.AddChannelArgument(GRPC_ARG_MAX_CONNECTION_AGE_MS, 3600000);
        
        // 2. MaxConnectionAgeGrace: Час (30 с) на завершення активних стримів після GOAWAY
        builder.AddChannelArgument(GRPC_ARG_MAX_CONNECTION_AGE_GRACE_MS, 30000);
        
        // 3. Keepalive настройки для виявлення "мертвих" Wi-Fi сокетів
        builder.AddChannelArgument(GRPC_ARG_KEEPALIVE_TIME_MS, 30000);
        builder.AddChannelArgument(GRPC_ARG_KEEPALIVE_TIMEOUT_MS, 10000);
        builder.AddChannelArgument(GRPC_ARG_KEEPALIVE_PERMIT_WITHOUT_CALLS, 1);

        std::unique_ptr<grpc::Server> server = builder.BuildAndStart();
        std::cout << "gRPC Ingest Server запущено на " << listen_addr << std::endl;
        return server;
    }
};
```
```go
// Go: Налаштування gRPC Сервера з параметрами Keepalive та Graceful GOAWAY
package main

import (
	"fmt"
	"net"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/keepalive"
)

func NewIngestServer(port int) (*grpc.Server, net.Listener, error) {
	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", port))
	if err != nil {
		return nil, nil, err
	}

	// Серверні параметри ротації та збереження з'єднань
	kaParams := keepalive.ServerParameters{
		MaxConnectionAge:      1 * time.Hour,  // Через 1 годину надсилається HTTP/2 GOAWAY
		MaxConnectionAgeGrace: 30 * time.Second, // 30 секунд на завершення поточних RPC
		Time:                  30 * time.Second, // PING інтервал перевірки сокета
		Timeout:               10 * time.Second, // Таймаут очікування PING ACK
	}

	srv := grpc.NewServer(
		grpc.KeepaliveParams(kaParams),
	)

	return srv, lis, nil
}
```
```py
# Python: AsyncIO gRPC Сервер з підтримкою ротації з'єднань
import asyncio
import grpc

async def serve_ingest(port: int):
    options = [
        ('grpc.max_connection_age_ms', 3600000),         # 1 година до GOAWAY
        ('grpc.max_connection_age_grace_ms', 30000),     # 30 секунд grace period
        ('grpc.keepalive_time_ms', 30000),               # Ping кожні 30 с
        ('grpc.keepalive_timeout_ms', 10000),            # Таймаут відповіді 10 с
        ('grpc.keepalive_permit_without_calls', 1),
    ]
    
    server = grpc.aio.server(options=options)
    server.add_insecure_port(f'[::]:{port}')
    await server.start()
    print(f"gRPC Ingest Server запущено на порту {port}")
    await server.wait_for_termination()
```
```ts
// TypeScript / Node.js: gRPC Client Config з передачею metadata home_id
import * as grpc from '@grpc/grpc-js';

export function createIngestClient(target: string, homeId: string): grpc.Client {
  const options: grpc.ClientOptions = {
    'grpc.keepalive_time_ms': 30000,
    'grpc.keepalive_timeout_ms': 10000,
    'grpc.keepalive_permit_without_calls': 1,
  };

  const client = new grpc.Client(target, grpc.credentials.createInsecure(), options);
  
  // Додаємо x-home-id у метадані виклику за замовчуванням
  const metadata = new grpc.Metadata();
  metadata.add('x-home-id', homeId);

  return client;
}
```
:::

## 3. Крок за кроком: Послідовність обробки GOAWAY та ротації сокета

Щоб краще зрозуміти роботу механізму Connection Draining, простежимо ланцюжок подій у часі між сервером Envoy, хабом Digital Homes та балансувальником L4:

1. **Ініціалізація та відлік часу:** Коли хаб створює нове gRPC-з'єднання до Envoy, таймер `max_connection_duration` починає відлік. З'єднання активне, кадри DATA вільно проходять в обидва боки.
2. **Відправка першого GOAWAY (Warning Phase):** Коли таймер вичерпує 3600 секунд, Envoy надсилає хабу перший кадр `GOAWAY` з унікальним `last_stream_id = 2^31 - 1`. Це повідомляє хаб про майбутнє закриття з'єднання, але дозволяє продовжувати надсилати RPC.
3. **Відправка другого GOAWAY (Drain Phase):** Одразу після цього Envoy надсилає другий кадр `GOAWAY` з точним значенням останнього прийнятого `stream_id` (наприклад, `stream_id = 42`). Усі стрими з ідентифікаторами, вищими за 42, хабом припиняються.
4. **Виконання активних викликів:** Хаб чекає завершення відповіді на стрим 42. Нові виклики (наприклад, стрим 44) хаб направляє у новий транспортний канал, який він паралельно відкриває до вхідного балансувальника.
5. **Завершення TCP-сокета:** Після отримання відповіді на стрим 42 хаб відправляє кадр `FIN` у TCP-сокет. Envoy підтверджує закриття. Старе з'єднання повністю вивільняє ресурси пам'яті.

## 4. Практичні нюанси та критичні пастки реалізації

### Синхронний MaxConnectionAge (Сплеск Thundering Herd)
Якщо 100 000 хабів підключилися одночасно під час відновлення мережі після блекауту і сервер має жорстко заданий параметр `MaxConnectionAge = 3600s` без використання джиттеру, то рівно через 3600 секунд усі 100 000 хабів отримають кадр `GOAWAY` в одну й ту ж секунду. 

Це викликає миттєвий шторм перепідключень (Thundering Herd) та повторний масовий TLS Handshake, який здатен покласти CPU на вхідних шлюзах. 

*Архітектурне правило:* На боці балансувальника або клієнтського фреймворку обов'язково вмикають випадковий зсув (jitter ±15%). В результаті `MaxConnectionAge` розмазується у часове вікно між 51 та 69 хвилинами.

### Занадто короткий MaxConnectionAgeGrace
Якщо встановити значення `MaxConnectionAgeGrace` менше ніж 5 секунд, тривалі стрими передачі відеопотоку з камер або оновлення прошивки будуть примусово обірвані сервером із помилкою `UNAVAILABLE` (сигнал `RST_STREAM`). 

Для тривалих стримів значення Grace Period розраховують виходячи з максимального часу завершення атомарної транзакції (зазвичай від 15 до 30 секунд).

### Відсутність обробки GOAWAY на боці клієнта
Деякі старі або спрощені HTTP/2 бібліотеки для мікроконтролерів ігнорують кадри `GOAWAY` і продовжують надсилати нові DATA-фрейми в закритий сокет. Це призводить до серії помилок `STREAM_CLOSED` та падіння зв'язку. Перед впровадженням ротації необхідно переконатися, що стек gRPC на боці пристрою коректно обробляє `GOAWAY` і прозоро відкриває нове TCP-з'єднання.

### Вичерпання файлових дескрипторів (sysctl limits)
Кожен gRPC-сокет та проксі-з'єднання у Linux потребують файлового дескриптора (`file descriptor`). При обробці 100 000 одночасних підключень стандартний системний ліміт `nofile` (який за замовчуванням часто дорівнює 1024) призводить до негайної помилки `Too many open files`. На вузлах Envoy та Ingest обов'язково виставляють `/etc/security/limits.conf` та `sysctl fs.file-max` у значення не менше 1 048 576.
