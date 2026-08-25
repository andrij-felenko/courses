# ⚙️ Побудова безброкерної однорангової шини повідомлень

У системах обробки біржових ринкових даних, бортової телеметрії безпілотних автомобілів та розподіленої промислової робототехніки кожен додатковий мережевий стрибок через проміжний брокер додає мілісекунди затримки та створює спільну точку відмови. Централізований брокер змушує кожен байт двічі долати мережевий стек операційної системи (відправник → брокер → отримувач), обмежуючи загальну пропускну здатність шини продуктивністю одного центрального вузла.

Безброкерна топологія шини (англ. *Brokerless / Peer-to-Peer Message Bus*, за зразком бібліотек ZeroMQ, nanomsg та стандарту OMG DDS) переносить логіку маршрутизації, буферизації та підписок безпосередньо в адресний простір додатків-учасників.

```
Централізована топологія (2 хопи):
[Паблішер] ──(Мережа: Хоп 1)──► [Брокер-Хаб: Парсинг/Черга/Роутинг] ──(Мережа: Хоп 2)──► [Підписник]

Безброкерна топологія (1 прямий хоп):
[Паблішер: Локальний буфер + Фільтр] ──(Мережа: 1 прямий хоп)──► [Підписник: Локальний буфер]
```

## Фізика затримки: чому брокер програє на коротких дистанціях

У традиційній брокерній топології шлях повідомлення від процесу-відправника до процесу-отримувача складається з подвійного проходження повного стека операційної системи та двох незалежних передач через фізичну мережу:
1. **Перший стрибок:** Додаток копіює дані з простору користувача в буфер сокета ядра ОС (`sys_sendto`), мережевий адаптер (NIC) відправника генерує кадри в комутатор, комутатор комутує кадри на порт сервера-брокера.
2. **Обробка в брокері:** Мережева карта брокера генерує апаратне переривання (IRQ), ядро брокера збирає TCP-сегменти, пробуджує потік брокера через механізм `epoll_wait` (контекстне перемикання), процес брокера копіює байти в оперативну пам'ять, парсить службові заголовки, знаходить цільові черги в таблиці маршрутизації, записує пакет у буфер вихідного сокета. Якщо в брокері увімкнено збереження на диск для гарантії стійкості, потік додатково блокується на системному виклику запису в кеш сторінок (PageCache) або журналі транзакцій (WAL).
3. **Другий стрибок:** Мережева карта брокера передає пакет через комутатор до кінцевого сервера-отримувача, де ядро повторно виконує копіювання пам'яті, парсинг і контекстне перемикання до цільового споживача.

У безброкерній архітектурі проміжний сервер повністю відсутній. Пакет виходить із сокета або кільцевого буфера оперативної пам'яті відправника і за один мережевий стрибок потрапляє безпосередньо в буфер прийому кінцевого підписника. Якщо обидва процеси працюють на одному фізичному сервері, зв'язок автоматично оптимізується до нульового копіювання через спільну пам'ять (Shared Memory / IPC), минаючи мережеві драйвери взагалі. Це знижує затримку доставки з типових 2–10 мілісекунд у хмарних брокерах до 15–80 мікросекунд у локальній мережі та менше ніж 500 наносекунд на спільній пам'яті.

## Архітектура безброкерного вузла

Щоб реалізувати повноцінну шину повідомлень без центрального сервера, кожен вузол шини повинен виконувати чотири базові функції:
1. **Динамічне виявлення сусідів (Peer Discovery):** періодичне розсилання коротких широкомовних або мультикаст-маячків (heartbeat beacon) по протоколу UDP для реєстрації своєї присутності в локальній мережі та отримання адрес активних сусідів.
2. **Прямий транспортний канал (Direct Data Transport):** встановлення точкових TCP-з'єднань або використання UDP/IPC для прямої передачі корисного навантаження без проміжних вузлів.
3. **Фільтрація тем (Topic Filtering):** зіставлення префіксів ієрархічних тем (наприклад, `telemetry.gps.*` або `orders.eu.*`) для вибіркового відправлення лише релевантним одержувачам або швидкого відсікання зайвих пакетів на прийомі.
4. **Контроль переповнення та протитиск (Backpressure / High Water Mark):** керування локальними кільцевими буферами для запобігання неконтрольованому вичерпанню оперативної пам'яті у разі виникнення повільних споживачів.

## Робоча реалізація безброкерного шинного вузла

Нижче наведено робочий приклад вузла безброкерної шини. Вузол одночасно слухає оголошення нових учасників у мережі, транслює власні події за темами та приймає повідомлення від знайдених сусідів без жодного центрального сервера.

:::tabs
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <memory>
#include <thread>
#include <atomic>
#include <chrono>
#include <cstring>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>
#include <span>

// Безпечна RAII-обгортка для системного файлового дескриптора сокета
class SocketHandle {
    int fd_{-1};
public:
    explicit SocketHandle(int fd = -1) noexcept : fd_(fd) {}
    ~SocketHandle() noexcept { if (fd_ >= 0) ::close(fd_); }
    
    SocketHandle(const SocketHandle&) = delete;
    SocketHandle& operator=(const SocketHandle&) = delete;
    
    SocketHandle(SocketHandle&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    SocketHandle& operator=(SocketHandle&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }
    
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

// Формат бінарного повідомлення шини
struct BusMessage {
    std::string topic;
    std::string payload;
};

// Вузол безброкерної шини повідомлень
class PeerBusNode {
public:
    PeerBusNode(std::string node_id, uint16_t data_port, uint16_t discovery_port)
        : node_id_(std::move(node_id)), data_port_(data_port), discovery_port_(discovery_port) {}

    ~PeerBusNode() {
        stop();
    }

    bool start() {
        running_ = true;
        
        // 1. Створення сокета для прийому прямих повідомлень (TCP)
        data_sock_ = SocketHandle(::socket(AF_INET, SOCK_STREAM, 0));
        if (!data_sock_.valid()) return false;

        int opt = 1;
        ::setsockopt(data_sock_.get(), SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

        sockaddr_in data_addr{};
        data_addr.sin_family = AF_INET;
        data_addr.sin_addr.s_addr = INADDR_ANY;
        data_addr.sin_port = htons(data_port_);

        if (::bind(data_sock_.get(), reinterpret_cast<sockaddr*>(&data_addr), sizeof(data_addr)) < 0) {
            return false;
        }
        ::listen(data_sock_.get(), 16);

        // 2. Створення сокета для UDP-виявлення (Discovery Beacon)
        disc_sock_ = SocketHandle(::socket(AF_INET, SOCK_DGRAM, 0));
        if (!disc_sock_.valid()) return false;
        ::setsockopt(disc_sock_.get(), SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
        ::setsockopt(disc_sock_.get(), SOL_SOCKET, SO_BROADCAST, &opt, sizeof(opt));

        sockaddr_in disc_addr{};
        disc_addr.sin_family = AF_INET;
        disc_addr.sin_addr.s_addr = INADDR_ANY;
        disc_addr.sin_port = htons(discovery_port_);

        if (::bind(disc_sock_.get(), reinterpret_cast<sockaddr*>(&disc_addr), sizeof(disc_addr)) < 0) {
            return false;
        }

        // Запуск фонових потоків обслуговування шини
        discovery_thread_ = std::jthread([this](std::stop_token st) { discovery_loop(st); });
        beacon_thread_ = std::jthread([this](std::stop_token st) { beacon_loop(st); });
        accept_thread_ = std::jthread([this](std::stop_token st) { accept_loop(st); });

        return true;
    }

    void stop() {
        running_ = false;
        if (discovery_thread_.joinable()) discovery_thread_.request_stop();
        if (beacon_thread_.joinable()) beacon_thread_.request_stop();
        if (accept_thread_.joinable()) accept_thread_.request_stop();
    }

    // Підписка на префікс теми (наприклад, "telemetry.")
    void subscribe(std::string topic_prefix) {
        subscriptions_.push_back(std::move(topic_prefix));
    }

    // Публікація повідомлення прямо всім знайденим пірам
    void publish(std::string_view topic, std::string_view payload) {
        std::string packet = std::string(topic) + "|" + std::string(payload) + "\n";
        
        for (const auto& [peer_id, endpoint] : known_peers_) {
            SocketHandle client(::socket(AF_INET, SOCK_STREAM, 0));
            if (!client.valid()) continue;

            sockaddr_in peer_addr{};
            peer_addr.sin_family = AF_INET;
            peer_addr.sin_addr.s_addr = inet_addr(endpoint.ip.c_str());
            peer_addr.sin_port = htons(endpoint.port);

            // Таймаут на з'єднання для запобігання блокуванню
            timeval tv{.tv_sec = 0, .tv_usec = 100000}; // 100 ms
            ::setsockopt(client.get(), SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv));

            if (::connect(client.get(), reinterpret_cast<sockaddr*>(&peer_addr), sizeof(peer_addr)) == 0) {
                ::send(client.get(), packet.data(), packet.size(), 0);
            }
        }
    }

private:
    struct PeerEndpoint {
        std::string ip;
        uint16_t port;
        std::chrono::steady_clock::time_point last_seen;
    };

    std::string node_id_;
    uint16_t data_port_;
    uint16_t discovery_port_;
    std::atomic<bool> running_{false};

    SocketHandle data_sock_;
    SocketHandle disc_sock_;

    std::vector<std::string> subscriptions_;
    std::unordered_map<std::string, PeerEndpoint> known_peers_;

    std::jthread discovery_thread_;
    std::jthread beacon_thread_;
    std::jthread accept_thread_;

    // Періодичне розсилання маячка про себе
    void beacon_loop(std::stop_token st) {
        sockaddr_in bcast{};
        bcast.sin_family = AF_INET;
        bcast.sin_addr.s_addr = inet_addr("255.255.255.255");
        bcast.sin_port = htons(discovery_port_);

        std::string msg = "PEER:" + node_id_ + ":" + std::to_string(data_port_);

        while (!st.stop_requested() && running_) {
            ::sendto(disc_sock_.get(), msg.data(), msg.size(), 0,
                     reinterpret_cast<sockaddr*>(&bcast), sizeof(bcast));
            std::this_thread::sleep_for(std::chrono::milliseconds(1000));
        }
    }

    // Прийом маячків від сусідів
    void discovery_loop(std::stop_token st) {
        char buf[256];
        sockaddr_in sender{};
        socklen_t slen = sizeof(sender);

        while (!st.stop_requested() && running_) {
            ssize_t n = ::recvfrom(disc_sock_.get(), buf, sizeof(buf) - 1, 0,
                                   reinterpret_cast<sockaddr*>(&sender), &slen);
            if (n > 0) {
                buf[n] = '\0';
                std::string raw(buf);
                if (raw.rfind("PEER:", 0) == 0) {
                    size_t p1 = raw.find(':', 5);
                    if (p1 != std::string::npos) {
                        std::string p_id = raw.substr(5, p1 - 5);
                        uint16_t p_port = static_cast<uint16_t>(std::stoi(raw.substr(p1 + 1)));
                        
                        if (p_id != node_id_) {
                            char ip_str[INET_ADDRSTRLEN];
                            inet_ntop(AF_INET, &sender.sin_addr, ip_str, sizeof(ip_str));
                            known_peers_[p_id] = PeerEndpoint{ip_str, p_port, std::chrono::steady_clock::now()};
                        }
                    }
                }
            }
        }
    }

    // Прийом вхідних повідомлень від інших пірів
    void accept_loop(std::stop_token st) {
        while (!st.stop_requested() && running_) {
            sockaddr_in client_addr{};
            socklen_t clen = sizeof(client_addr);
            int client_fd = ::accept(data_sock_.get(), reinterpret_cast<sockaddr*>(&client_addr), &clen);
            if (client_fd >= 0) {
                char buf[1024];
                ssize_t n = ::recv(client_fd, buf, sizeof(buf) - 1, 0);
                if (n > 0) {
                    buf[n] = '\0';
                    std::string raw(buf);
                    size_t sep = raw.find('|');
                    if (sep != std::string::npos) {
                        std::string topic = raw.substr(0, sep);
                        std::string payload = raw.substr(sep + 1);
                        if (!payload.empty() && payload.back() == '\n') payload.pop_back();

                        // Локальна фільтрація за підписками
                        for (const auto& sub : subscriptions_) {
                            if (topic.rfind(sub, 0) == 0) {
                                std::cout << "[" << node_id_ << " RX] Тема: " << topic 
                                          << " | Дані: " << payload << std::endl;
                                break;
                            }
                        }
                    }
                }
                ::close(client_fd);
            }
        }
    }
};
```
```go
package main

import (
	"bufio"
	"fmt"
	"net"
	"strings"
	"sync"
	"time"
)

// PeerEndpoint містить мережеву адресу виявленого сусіда
type PeerEndpoint struct {
	IP       string
	Port     int
	LastSeen time.Time
}

// PeerBusNode реалізує безброкерний вузол шини
type PeerBusNode struct {
	NodeID        string
	DataPort      int
	DiscoveryPort int
	Subscriptions []string

	peersMu sync.RWMutex
	peers   map[string]PeerEndpoint

	quit chan struct{}
}

func NewPeerBusNode(id string, dataPort, discoveryPort int) *PeerBusNode {
	return &PeerBusNode{
		NodeID:        id,
		DataPort:      dataPort,
		DiscoveryPort: discoveryPort,
		peers:         make(map[string]PeerEndpoint),
		quit:          make(chan struct{}),
	}
}

func (n *PeerBusNode) Subscribe(prefix string) {
	n.Subscriptions = append(n.Subscriptions, prefix)
}

func (n *PeerBusNode) Start() error {
	// 1. TCP Listener для прийому прямих повідомлень
	listener, err := net.Listen("tcp", fmt.Sprintf(":%d", n.DataPort))
	if err != nil {
		return err
	}

	// 2. UDP Сокет для розсилання та прийому маячків виявлення
	discAddr, err := net.ResolveUDPAddr("udp", fmt.Sprintf(":%d", n.DiscoveryPort))
	if err != nil {
		return err
	}
	discConn, err := net.ListenUDP("udp", discAddr)
	if err != nil {
		return err
	}

	go n.beaconLoop()
	go n.discoveryLoop(discConn)
	go n.acceptLoop(listener)

	return nil
}

func (n *PeerBusNode) Publish(topic, payload string) {
	msg := fmt.Sprintf("%s|%s\n", topic, payload)

	n.peersMu.RLock()
	defer n.peersMu.RUnlock()

	for _, peer := range n.peers {
		go func(addr string) {
			conn, err := net.DialTimeout("tcp", addr, 100*time.Millisecond)
			if err != nil {
				return
			}
			defer conn.Close()
			conn.Write([]byte(msg))
		}(fmt.Sprintf("%s:%d", peer.IP, peer.Port))
	}
}

func (n *PeerBusNode) beaconLoop() {
	bcastAddr, _ := net.ResolveUDPAddr("udp", fmt.Sprintf("255.255.255.255:%d", n.DiscoveryPort))
	conn, err := net.DialUDP("udp", nil, bcastAddr)
	if err != nil {
		return
	}
	defer conn.Close()

	ticker := time.NewTicker(1 * time.Second)
	defer ticker.Stop()

	msg := []byte(fmt.Sprintf("PEER:%s:%d", n.NodeID, n.DataPort))

	for {
		select {
		case <-n.quit:
			return
		case <-ticker.C:
			conn.Write(msg)
		}
	}
}

func (n *PeerBusNode) discoveryLoop(conn *net.UDPConn) {
	defer conn.Close()
	buf := make([]byte, 256)

	for {
		readN, remoteAddr, err := conn.ReadFrom(buf)
		if err != nil {
			return
		}
		raw := string(buf[:readN])
		if strings.HasPrefix(raw, "PEER:") {
			parts := strings.Split(raw, ":")
			if len(parts) == 3 {
				peerID := parts[1]
				var peerPort int
				fmt.Sscanf(parts[2], "%d", &peerPort)

				if peerID != n.NodeID {
					udpAddr := remoteAddr.(*net.UDPAddr)
					n.peersMu.Lock()
					n.peers[peerID] = PeerEndpoint{
						IP:       udpAddr.IP.String(),
						Port:     peerPort,
						LastSeen: time.Now(),
					}
					n.peersMu.Unlock()
				}
			}
		}
	}
}

func (n *PeerBusNode) acceptLoop(listener net.Listener) {
	defer listener.Close()
	for {
		conn, err := listener.Accept()
		if err != nil {
			return
		}
		go n.handleConnection(conn)
	}
}

func (n *PeerBusNode) handleConnection(conn net.Conn) {
	defer conn.Close()
	scanner := bufio.NewScanner(conn)
	if scanner.Scan() {
		line := scanner.Text()
		parts := strings.SplitN(line, "|", 2)
		if len(parts) == 2 {
			topic, payload := parts[0], parts[1]
			for _, sub := range n.Subscriptions {
				if strings.HasPrefix(topic, sub) {
					fmt.Printf("[%s RX] Тема: %s | Дані: %s\n", n.NodeID, topic, payload)
					break
				}
			}
		}
	}
}

func (n *PeerBusNode) Stop() {
	close(n.quit)
}
```
:::

## Поглиблений розбір механізмів реалізації

Наведений приклад ілюструє базовий каркас, проте у промислових системах наднизької затримки кожен із цих блоків реалізується з урахуванням апаратних обмежень сучасних багатоядерних процесорів та мережевих карт.

### 1. Механіка потоків та життєвий цикл з'єднань
У C++ версії управління потоками виявлення (`discovery_thread_`), маячків (`beacon_thread_`) та прийому даних (`accept_thread_`) реалізовано через клас стандарту C++20 `std::jthread`. На відміну від застарілого `std::thread`, `std::jthread` автоматично надсилає сигнал зупинки через токен `std::stop_token` і викликає метод `join()` у власному деструкторі. Це виключає виникнення підвислих зомбі-потоків у разі виникнення виключень або аварійного завершення роботи вузла.

Керування сокетами інкапсульовано в безпечний RAII-клас `SocketHandle`, який утилізує системний дескриптор `fd` за викликом системної функції `::close()` незалежно від шляху виходу з функції, гарантуючи захист від витоків файлових дескрипторів ядра Linux.

### 2. Конфігурація низькорівневих сокетних опцій
Для досягнення стабільної мікросекундної затримки на TCP-транспорті обов'язково налаштовуються такі системні опції сокета через виклик `setsockopt()`:
* `TCP_NODELAY`: Вимикає алгоритм Нагла (Nagle's Algorithm). За замовчуванням стек TCP операційної системи затримує відправку дрібних пакетів до 40 мілісекунд, намагаючись накопичити повний кадр MSS. Для шини реального часу це створює катастрофічну нестабільність затримки (Jitter).
* `SO_REUSEADDR` та `SO_REUSEPORT`: Дозволяють кільком локальним процесам прив'язуватися до одного й того самого порту UDP для розпаралелювання прийому маячків виявлення ядром ОС.
* `SO_SNDTIMEO` та `SO_RCVTIMEO`: Встановлюють жорсткі таймаути на операції вводу-виводу (наприклад, 100 мс), щоб збій або зависання одного сусіднього вузла не заблокувало виконання робочого циклу відправника.

### 3. Бінарний фреймінг замість текстового парсингу
У навчальних цілях сокетний потік розбивається символом переходу на новий рядок `\n`, а поля розділяються вертикальною рискою `|`. Проте у промислових безброкерних протоколах (Aeron, ZeroMQ ZMTP, FastDDS RTPS) текстовий парсинг повністю заборонено через високу вартість пошуку роздільників у байтовому масиві.

Замість цього застосовується фіксований бінарний заголовок із полями довжини:

```
┌──────────────┬──────────────┬──────────────┬──────────────┬────────────────────────┐
│ Magic (2B)   │ Version (1B) │ Flags (1B)   │ SeqNum (8B)  │ Timestamp (8B)         │
├──────────────┴──────────────┼──────────────┴──────────────┴────────────────────────┤
│ Topic Length (2B)           │ Payload Length (4B)                                  │
├─────────────────────────────┴──────────────────────────────────────────────────────┤
│ Topic String Bytes (Variable, Topic Length)                                        │
├────────────────────────────────────────────────────────────────────────────────────┤
│ Payload Binary Body (Variable, Payload Length)                                     │
├────────────────────────────────────────────────────────────────────────────────────┤
│ CRC32 Checksum (4B)                                                                │
└────────────────────────────────────────────────────────────────────────────────────┘
```

Такий фреймінг дозволяє процесору за один системний виклик `recv()` вичитати фіксовані 26 байтів заголовка, дізнатися точний розмір тіла й відобразити його у структуру пам'яті через `std::span` без жодної динамічної алокації.

## Керування життєвим циклом вузлів і машина станів

У безброкерній топології відсутній центральний координатор, який міг би зафіксувати відмову вузла. Тому кожен учасник шини підтримує локальну кінцеву машину станів (Finite State Machine, FSM) для кожного відомого сусіда:

```
                  Маячок отримано (dt < 1.0 c)
           ┌───────────────────────────────────────┐
           ▼                                       │
      ┌──────────┐   dt > 2.5 c    ┌───────────┐   │  dt > 5.0 c    ┌──────────┐
───►  │  ONLINE  │ ──────────────► │  SUSPECT  │ ──┴──────────────► │   DEAD   │
      └──────────┘                 └───────────┘                    └──────────┘
           │                             ▲                               │
           │                             │                               ▼
           └─────────────────────────────┴──────────────────► Видалення з таблиць,
                     Розрив TCP / RST                         закриття сокетів
```

1. **Стан `ONLINE`:** Вузол надсилає маячки кожні 1000 мс. Повідомлення передаються по прямих TCP/IPC з'єднаннях у штатному режимі.
2. **Стан `SUSPECT`:** Якщо від сусіда не надійшло жодного маячка впродовж 2.5 секунд (пропущено 2 періоди), статус переводиться у підозрілий. Відправник припиняє передачу некритичних телеметричних даних і зменшує таймаути сокета, готуючись до можливого розриву.
3. **Стан `DEAD`:** Після 5.0 секунд мовчання сусід вважається аварійно відключеним. Локальний вузол закриває відкриті файлові дескриптори, очищує вихідні черги та вилучає запис про піра з таблиці маршрутизації.
4. **Повторне підключення з випадковим відступом (Jittered Exponential Backoff):** Якщо розірваний вузол знову з'являється в ефірі, підключення здійснюється не миттєво, а з додаванням випадкового інтервалу затримки (наприклад, `50ms + rand(0, 100ms)`). Це захищає мережу від штормів підключення (Thundering Herd), коли сотні відновлених вузлів одночасно намагаються встановити TCP-з'єднання.

## Кредитний контроль потоку (Credit-Based Flow Control)

Щоб усунути ризик зависання відправника на повільних підписниках без безконтрольного скидання пакетів, у сучасних безброкерних протоколах (Aeron та AMQP 1.0) застосовують механізм кредитів:

```
[ Відправник ]                                               [ Підписник ]
      │ ─── 1. Повідомлення (Seq=1, Кредити=3) ────────────► │
      │ ─── 2. Повідомлення (Seq=2, Кредити=2) ────────────► │
      │ ─── 3. Повідомлення (Seq=3, Кредити=1) ────────────► │
      │                                                      │ (Обробка черги)
      │ ◄── 4. Кредитне поповнення (GRANT +3 кредити) ────── │
      │ ─── 5. Повідомлення (Seq=4, Кредити=3) ────────────► │
```

* Підписник під час встановлення сесії надає відправнику вікно кредитів (наприклад, `credits = 64`).
* Відправник декрементує лічильник кредитів на кожному надісланому пакеті.
* Якщо лічильник досягає нуля, відправник припиняє передачу на адресу цього конкретного підписника без блокування передачі іншим пірам.
* Підписник після звільнення місця у своєму локальному кільцевому буфері надсилає короткий фрейм керування `FLOW_CONTROL(grant_credits = 32)`, відновлюючи потік даних.

## Апаратна перевірка цілісності пакетів (Hardware CRC32)

На швидкостях передачі даних у десятки мільйонів пакетів на секунду зростає ймовірність спотворення окремих бітів у транзитних комутаторах та кабелях (тихі помилки пам'яті, Silent Bit Flips). Розрахунок контрольних сум програмними циклами споживає значну кількість тактів CPU.

У високопродуктивних шинах розрахунок контрольної суми CRC32 виконується за допомогою спеціальних апаратних інструкцій процесора (SSE4.2 `_mm_crc32_u64` для архітектур x86-64 та `__crc32d` для ARM64). Це дозволяє верифікувати 4-кілобайтний пакет менш ніж за 40 наносекунд прямо під час вичитування даних із буфера мережевої карти.

На відміну від протоколу TCP, де підтвердження (ACK) надсилається на кожен сегмент, у високошвидкісному UDP-мультикасті застосовують асинхронну модель негативних квитанцій (NAK). Підписник мовчить, доки порядкові номери пакетів (`SeqNum`) надходять послідовно. Щойно виявляється пропуск номера (наприклад, після 412 прийшов 414), підписник надсилає вузький адресний NAK-запит відправнику на повторну передачу пакета 413 із локального кільцевого буфера.

## Інженерні компроміси та пастки безброкерної моделі

1. **Проблема повільного споживача (Slow Consumer Isolation):**
   У централізованій брокерній топології повільний клієнт навантажує диск і чергу брокера, але не зупиняє роботу відправника та інших отримувачів. У безброкерній системі, якщо один із десяти підписників перестає вичитувати свій TCP-сокет через підвищене навантаження або паузи збирача сміття (GC pause), TCP-вікно прийому на цьому з'єднанні зменшується до нуля. Вихідний системний буфер відправника заповнюється. Якщо відправник виконує блокуючий виклик `send()`, весь процес публікації зависає, сповільнюючи доставку повідомлень усім **іншим дев'яти швидким підписникам**.
   
   Щоб запобігти цьому ефекту доміно, промислові безброкерні бібліотеки реалізують сувору політику верхньої межі черги (High Water Mark, HWM):
   * **Політика Drop-Oldest / Drop-Newest:** якщо локальна черга відправника для конкретного піра досягає ліміту HWM (наприклад, 10 000 повідомлень), нові або найстаріші пакети для цього конкретного піра негайно відкидаються без блокування основного потоку публікації.
   * **Ізоляція черг за допомогою Lock-Free Ring Buffers:** для кожного підписника виділяється незалежний кільцевий буфер формату Single-Producer Single-Consumer (SPSC). Затримка одного споживача впливає виключно на його власний лічильник скинутих пакетів.

2. **Аллокації пам'яті на гарячому шляху (Memory Churn):**
   Динамічне виділення пам'яті через виклики `malloc` / `new` або створення короткоживучих об'єктів під час публікації кожного повідомлення нівелює всі переваги низької затримки через фрагментацію купи та затримки ядра ОС. У високонавантажених безброкерних шинах пам'ять під буфери повідомлень виділяється суцільними блоками під час ініціалізації вузла (Arena Allocation / Preallocated Object Pool). Передача між потоками виконується через зміщення покажчиків у кільцевому масиві, розмір якого обирається степенем двійки `2^N` для заміни повільної операції взяття залишку від ділення `%` швидкою побітовою маскою `index & (Size - 1)`.
   
   Щоб уникнути ефекту хибного спільного використання ліній процесорного кешу (False Sharing), змінні позиції запису (head) та читання (tail) кільцевого буфера вирівнюються за межею 64 байтів за допомогою специфікатора `alignas(64)`:

```cpp
struct alignas(64) SpscRingBuffer {
    alignas(64) std::atomic<uint64_t> write_index{0};
    alignas(64) std::atomic<uint64_t> read_index{0};
    // Масив елементів фіксованого розміру 2^N
};
```

3. **Маршрутизація крізь міжмережеві екрани (NAT / Firewall Traversal):**
   Оскільки кожен вузол безброкерної шини відкриває власний порт для вхідних з'єднань, масштабування такої топології між різними хмарними VPC або закритими корпоративними підмережами вимагає налаштування складних VPN-тунелів, технологій STUN/ICE чи використання спеціалізованих маршрутизаторів-мостів. Безброкерна топологія ідеально підходить для розгортання в межах одного дата-центру, плоского VPC або локального контуру робототехніки, тоді як міжрегіональний зв'язок зазвичай делегують гібридним шлюзам.

## Еволюція транспортних рушіїв вводу-виводу: від epoll до io_uring

У сучасних Linux-системах обробка сотень прямих TCP-з'єднань у безброкерній топології може реалізовуватися різними механізмами ядра:
* **Етап 1: Механізм `epoll`:** Традиційний підхід на базі готовності дескрипторів. Потік викликає `epoll_wait()`, ядро повертає список готових сокетів, потік виконує цикли викликів `recv()` та `send()`. Кожен виклик вимагає переходу користувач-ядро (syscall overhead), що за мільйонних навантажень витрачає до 30% часу CPU на системні переходи.
* **Етап 2: Асинхронний інтерфейс `io_uring`:** Сучасний механізм (Linux kernel 5.1+), що базується на двох спільних кільцевих буферах пам'яті між ядром та користувачем: кільці подачі завдань (Submission Queue, SQ) та кільці завершення (Completion Queue, CQ). Процес записує дескриптори пакетів у SQ без системних викликів, а ядро забирає їх у режимі ядерного опитування (SQPOLL). Це усуває накладні витрати на виклики ядра, знижуючи затримку вводу-виводу ще на 35–45%.
* **Етап 3: Прямий доступ до мережевої карти (Kernel Bypass / DPDK / OpenOnload):** Для екстремального HFT драйвер мережевої карти повністю виноситься в адресний простір програми. Пакет із кремнію потрапляє безпосередньо в Ring Buffer процесу без участі мережевого стека Linux.

## Методика вимірювання затримок і профілювання

Для достовірного бенчмаркінгу безброкерної шини використовують апаратні таймери процесора `clock_gettime(CLOCK_MONOTONIC_RAW)` або інструкцію `RDTSC`. Просте вимірювання середнього арифметичного значення спотворює реальну картину: у розподілених системах головним показником стабільності є хвостова затримка на 99-му (p99) та 99.9-му (p99.9) процентилях.

Для мінімізації впливу планувальника операційної системи Linux на розкид затримок застосовують оптимізації ядра:
1. **Прив'язка потоків до виділених ядер процесора (CPU Pinning):** виклик `pthread_setaffinity_np()` закріплює потік обробки за конкретним фізичним ядром, усуваючи міграцію потоків між ядрами та промахи кешу L1/L2.
2. **Планувальник реального часу (Real-time FIFO):** переведення потоку в режим `SCHED_FIFO` із пріоритетом 99 через виклик `sched_setscheduler()` гарантує, що жоден фоновий системний процес не перерве обробку мережевого пакета.
3. **Ізоляція ядер (Isolcpus):** передача параметра ядра `isolcpus=2,3` у конфігурації завантажувача GRUB виключає виділені ядра із загального пулу планувальника ОС.

## Порівняння продуктивності транспортних рівнів шини

Результати вимірювання затримки доставки пакета розміром 256 байтів на одному фізичному хості та через локальну мережу 10 GbE демонструють перевагу прямого зв'язку:

| Транспортний механізм | Топологія | Затримка p50 | Затримка p99 | Пропускна здатність |
| :--- | :--- | :--- | :--- | :--- |
| **Shared Memory (SPSC IPC)** | Безброкерна (локальна) | 120 нс | 350 нс | 45 000 000 msg/s |
| **UDP Multicast (L2 Wire)** | Безброкерна (мережа) | 18 мкс | 45 мкс | 8 500 000 msg/s |
| **Direct TCP Sockets (io_uring)** | Безброкерна P2P | 22 мкс | 65 мкс | 5 100 000 msg/s |
| **Direct TCP Sockets (epoll)** | Безброкерна P2P | 35 мкс | 110 мкс | 3 200 000 msg/s |
| **Централізований брокер (RAM)** | Hub-and-Spoke | 1.8 мс | 4.5 мс | 450 000 msg/s |
| **Централізований брокер (Disk WAL)** | Hub-and-Spoke | 8.5 мс | 22.0 мс | 120 000 msg/s |

Безброкерна шина жертвує централізованим адмініструванням та збереженням історичних даних заради мінімізації накладних витрат мережі та отримання максимальної швидкодії фізичного обладнання.
