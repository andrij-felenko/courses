# ⚙️ Реалізація вузла Thread та передача UDP-телеметрії через OpenThread API

Розробка бездротового вузла Інтернету речей на базі протоколу Thread потребує глибокого розуміння асинхронної подієвої архітектури стеку, коректного налаштування криптографічних параметрів безпеки, керування буферами повідомлень операційної системи реального часу (RTOS) та використання стандартизованих протоколів прикладного рівня. Еталонний відкритий стек **OpenThread** спроєктований так, щоб працювати на апаратно обмежених мікроконтролерах із мінімальним обсягом оперативної пам'яті (від 32 КБ RAM та 128 КБ Flash), використовуючи статичне виділення пулів пам'яті та кооперативну багатозадачність на базі тасклетів (*Tasklets*).

Для підключення автономного пристрою (наприклад, на базі чіпів Nordic Semiconductor nRF52840, Espressif ESP32-H2 або Silicon Labs EFR32MG24) до захищеної мережі Thread необхідно виконати п'ять послідовних кроків:
1. **Ініціалізація екземпляра стеку:** створення структури `otInstance`, яка інкапсулює внутрішній стан усіх рівнів протоколу (PHY, MAC, 6LoWPAN, IPv6, MLE, Routing).
2. **Конфігурація активного робочого набору (Active Operational Dataset) або динамічне комісіонування:** внесення номера радіоканалу 2.4 ГГц, 16-бітного ідентифікатора мережі PAN ID, розширеного PAN ID та 128-бітного майстер-ключа безпеки Network Key (або автентифікація через пароль PSKd).
3. **Реєстрація обробників подій топології:** підключення функції зворотного виклику (State Changed Callback) для відстеження переходу вузла між станами `Detached`, `Child`, `Router` або `Leader`.
4. **Активація мережевих інтерфейсів:** увімкнення адаптера IPv6 та запуск протоколу маршрутизації Thread.
5. **Створення сокета UDP та реєстрація ресурсів CoAP:** відкриття кінцевої точки зв'язку для передачі та прийому корисного навантаження прикладного рівня.

---

### Робочий код вузла Thread (вкладки C та сучасний C++)

:::tabs
```c
#include <stdio.h>
#include <string.h>
#include <openthread/instance.h>
#include <openthread/ip6.h>
#include <openthread/thread.h>
#include <openthread/dataset.h>
#include <openthread/udp.h>
#include <openthread/coap.h>
#include <openthread/joiner.h>
#include <openthread/tasklet.h>

#define UDP_PORT 12345

static otInstance *s_instance = NULL;
static otUdpSocket s_socket;
static otCoapResource s_temp_resource;

/* Обробник вхідних UDP повідомлень */
static void handle_udp_receive(void *context, otMessage *message, const otMessageInfo *messageInfo)
{
    (void)context;
    char buf[128];
    uint16_t length = otMessageGetLength(message) - otMessageGetOffset(message);

    if (length >= sizeof(buf)) {
        length = sizeof(buf) - 1;
    }

    otMessageRead(message, otMessageGetOffset(message), buf, length);
    buf[length] = '\0';

    char ip_str[OT_IP6_ADDRESS_STRING_SIZE];
    otIp6AddressToString(&messageInfo->mPeerAddr, ip_str, sizeof(ip_str));

    printf("[UDP Rx] Від [%s]:%u -> %s\n", ip_str, messageInfo->mPeerPort, buf);
}

/* Обробник вхідного CoAP GET запиту /sensors/temp */
static void handle_coap_temp_request(void *context, otMessage *message, const otMessageInfo *messageInfo)
{
    otInstance *instance = (otInstance *)context;
    otCoapCode message_code = otCoapMessageGetCode(message);

    if (message_code == OT_COAP_CODE_GET) {
        otMessage *response = otCoapNewMessage(instance, NULL);
        if (!response) {
            return;
        }

        otCoapMessageInitResponse(response, message, OT_COAP_TYPE_ACKNOWLEDGMENT, OT_COAP_CODE_CONTENT);
        otCoapMessageSetFormat(response, OT_COAP_OPTION_CONTENT_FORMAT_TEXT_PLAIN);

        const char *payload = "{\"temp\": 23.5, \"unit\": \"C\"}";
        otCoapMessageSetPayloadMarker(response);
        otMessageAppend(response, payload, (uint16_t)strlen(payload));

        otCoapSendResponse(instance, response, messageInfo);
        printf("[CoAP] Відправлено відповідь на GET /sensors/temp\n");
    }
}

/* Зворотний виклик зміни ролі в мережі Thread */
static void handle_state_changed(otChangedFlags flags, void *context)
{
    (void)context;
    if (flags & OT_CHANGED_THREAD_ROLE) {
        otDeviceRole role = otThreadGetDeviceRole(s_instance);
        const char *role_str = "Unknown";

        switch (role) {
        case OT_DEVICE_ROLE_DISABLED: role_str = "Disabled (Вимкнено)"; break;
        case OT_DEVICE_ROLE_DETACHED: role_str = "Detached (Пошук мережі)"; break;
        case OT_DEVICE_ROLE_CHILD:    role_str = "Child (Кінцевий вузол)"; break;
        case OT_DEVICE_ROLE_ROUTER:   role_str = "Router (Маршрутизатор)"; break;
        case OT_DEVICE_ROLE_LEADER:   role_str = "Leader (Координатор мережі)"; break;
        }
        printf("[Thread] Зміна ролі -> %s\n", role_str);
    }
}

/* Налаштування параметрів мережі за замовчуванням */
static void configure_network_dataset(otInstance *instance)
{
    otOperationalDataset dataset;
    memset(&dataset, 0, sizeof(dataset));

    /* 1. Номер радіоканалу 2.4 ГГц (канали 11..26) */
    dataset.mChannel = 15;
    dataset.mComponents.mIsChannelPresent = true;

    /* 2. 16-бітний ідентифікатор PAN */
    dataset.mPanId = (otPanId)0x1234;
    dataset.mComponents.mIsPanIdPresent = true;

    /* 3. Мережевий майстер-ключ AES-128 (16 байтів) */
    const uint8_t master_key[OT_NETWORK_KEY_SIZE] = {
        0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,
        0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff
    };
    memcpy(dataset.mNetworkKey.m8, master_key, sizeof(master_key));
    dataset.mComponents.mIsNetworkKeyPresent = true;

    /* 4. Назва мережі */
    const char *net_name = "Thread-OpenLab";
    size_t name_len = strlen(net_name);
    memcpy(dataset.mNetworkName.m8, net_name, name_len);
    dataset.mNetworkName.m8[name_len] = '\0';
    dataset.mComponents.mIsNetworkNamePresent = true;

    /* Застосування активного набору конфігурації */
    otDatasetSetActive(instance, &dataset);
}

/* Відправка телеметрії за вказаною IPv6 адресою */
void send_telemetry(otInstance *instance, const char *dest_ip_str, uint16_t port, const char *payload)
{
    otMessageInfo message_info;
    memset(&message_info, 0, sizeof(message_info));

    otIp6AddressFromString(dest_ip_str, &message_info.mPeerAddr);
    message_info.mPeerPort = port;

    /* Виділення буфера з пулу OpenThread */
    otMessage *msg = otUdpNewMessage(instance, NULL);
    if (!msg) {
        printf("[Помилка] Не вдалося виділити буфер повідомлення\n");
        return;
    }

    if (otMessageAppend(msg, payload, (uint16_t)strlen(payload)) != OT_ERROR_NONE) {
        otMessageFree(msg);
        return;
    }

    /* Відправка пакета. У разі успіху OpenThread сам звільнить пам'ять msg */
    if (otUdpSend(instance, &s_socket, msg, &message_info) != OT_ERROR_NONE) {
        printf("[Помилка] Не вдалося відправити UDP пакет\n");
        otMessageFree(msg);
    } else {
        printf("[UDP Tx] Надіслано %u байтів до [%s]:%u\n", (unsigned)strlen(payload), dest_ip_str, port);
    }
}

int main(void)
{
    /* 1. Ініціалізація екземпляра OpenThread */
    s_instance = otInstanceInitSingle();
    if (!s_instance) {
        printf("[Фатальна помилка] Ініціалізація OpenThread зазнала невдачі\n");
        return -1;
    }

    /* 2. Реєстрація зворотного виклику стану мережі */
    otSetStateChangedCallback(s_instance, handle_state_changed, NULL);

    /* 3. Налаштування робочого набору параметрів */
    configure_network_dataset(s_instance);

    /* 4. Активація мережевого інтерфейсу IPv6 та протоколу Thread */
    otIp6SetEnabled(s_instance, true);
    otThreadSetEnabled(s_instance, true);

    /* 5. Відкриття та прив'язка UDP сокета */
    memset(&s_socket, 0, sizeof(s_socket));
    otUdpOpen(s_instance, &s_socket, handle_udp_receive, NULL);

    otSockAddr sock_addr;
    memset(&sock_addr, 0, sizeof(sock_addr));
    sock_addr.mPort = UDP_PORT;
    otUdpBind(s_instance, &s_socket, &sock_addr, OT_NETIF_THREAD);

    /* 6. Реєстрація CoAP-ресурсу */
    otCoapStart(s_instance, OT_DEFAULT_COAP_PORT);
    memset(&s_temp_resource, 0, sizeof(s_temp_resource));
    s_temp_resource.mUriPath = "sensors/temp";
    s_temp_resource.mHandler = handle_coap_temp_request;
    s_temp_resource.mContext = s_instance;
    otCoapAddResource(s_instance, &s_temp_resource);

    printf("Вузол Thread ініціалізовано. Очікування входження в мережу...\n");

    /* Головний асинхронний цикл обробки подій OpenThread */
    while (1) {
        otTaskletsProcess(s_instance);
        /* Якщо черга завдань порожня, переводимо мікроконтролер у сон */
        if (!otTaskletsArePending(s_instance)) {
            /* otSysProcessDrivers(...) / __WFI() */
        }
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <span>
#include <array>
#include <expected>
#include <cstring>
#include <stdexcept>
#include <openthread/instance.h>
#include <openthread/ip6.h>
#include <openthread/thread.h>
#include <openthread/dataset.h>
#include <openthread/udp.h>
#include <openthread/coap.h>
#include <openthread/joiner.h>
#include <openthread/tasklet.h>

namespace thread_mesh {

enum class DeviceRole {
    Disabled,
    Detached,
    Child,
    Router,
    Leader,
    Unknown
};

class ThreadNode {
public:
    ThreadNode() {
        instance_ = otInstanceInitSingle();
        if (!instance_) {
            throw std::runtime_error("Не вдалося ініціалізувати екземпляр OpenThread");
        }
        otSetStateChangedCallback(instance_, &ThreadNode::onStateChangedStatic, this);
    }

    ~ThreadNode() {
        if (coapStarted_) {
            otCoapStop(instance_);
        }
        if (socketOpened_) {
            otUdpClose(instance_, &socket_);
        }
        if (instance_) {
            otInstanceFinalize(instance_);
        }
    }

    ThreadNode(const ThreadNode&) = delete;
    ThreadNode& operator=(const ThreadNode&) = delete;
    ThreadNode(ThreadNode&&) noexcept = delete;
    ThreadNode& operator=(ThreadNode&&) noexcept = delete;

    void configureNetwork(uint16_t channel, uint16_t panId, 
                          std::span<const uint8_t, 16> networkKey, 
                          std::string_view networkName) 
    {
        otOperationalDataset dataset{};
        dataset.mChannel = channel;
        dataset.mComponents.mIsChannelPresent = true;

        dataset.mPanId = static_cast<otPanId>(panId);
        dataset.mComponents.mIsPanIdPresent = true;

        std::memcpy(dataset.mNetworkKey.m8, networkKey.data(), networkKey.size());
        dataset.mComponents.mIsNetworkKeyPresent = true;

        size_t nameLen = std::min(networkName.size(), sizeof(dataset.mNetworkName.m8) - 1);
        std::memcpy(dataset.mNetworkName.m8, networkName.data(), nameLen);
        dataset.mNetworkName.m8[nameLen] = '\0';
        dataset.mComponents.mIsNetworkNamePresent = true;

        otDatasetSetActive(instance_, &dataset);
    }

    void start() {
        otIp6SetEnabled(instance_, true);
        otThreadSetEnabled(instance_, true);
    }

    void openUdpPort(uint16_t port) {
        std::memset(&socket_, 0, sizeof(socket_));
        otUdpOpen(instance_, &socket_, &ThreadNode::onUdpReceiveStatic, this);
        
        otSockAddr sockAddr{};
        sockAddr.mPort = port;
        otUdpBind(instance_, &socket_, &sockAddr, OT_NETIF_THREAD);
        socketOpened_ = true;
    }

    void enableCoapService() {
        otCoapStart(instance_, OT_DEFAULT_COAP_PORT);
        std::memset(&tempResource_, 0, sizeof(tempResource_));
        tempResource_.mUriPath = "sensors/temp";
        tempResource_.mHandler = &ThreadNode::onCoapTempRequestStatic;
        tempResource_.mContext = this;
        otCoapAddResource(instance_, &tempResource_);
        coapStarted_ = true;
    }

    std::expected<void, otError> sendUdp(std::string_view destIp, uint16_t port, std::string_view payload) {
        otMessageInfo messageInfo{};
        otIp6AddressFromString(destIp.data(), &messageInfo.mPeerAddr);
        messageInfo.mPeerPort = port;

        otMessage *msg = otUdpNewMessage(instance_, nullptr);
        if (!msg) {
            return std::unexpected(OT_ERROR_NO_BUFS);
        }

        otError err = otMessageAppend(msg, payload.data(), static_cast<uint16_t>(payload.size()));
        if (err != OT_ERROR_NONE) {
            otMessageFree(msg);
            return std::unexpected(err);
        }

        err = otUdpSend(instance_, &socket_, msg, &messageInfo);
        if (err != OT_ERROR_NONE) {
            otMessageFree(msg);
            return std::unexpected(err);
        }

        return {};
    }

    void processTasks() {
        otTaskletsProcess(instance_);
    }

    bool hasPendingTasks() const noexcept {
        return otTaskletsArePending(instance_);
    }

private:
    static void onStateChangedStatic(otChangedFlags flags, void *context) {
        static_cast<ThreadNode*>(context)->onStateChanged(flags);
    }

    static void onUdpReceiveStatic(void *context, otMessage *msg, const otMessageInfo *info) {
        static_cast<ThreadNode*>(context)->onUdpReceive(msg, info);
    }

    static void onCoapTempRequestStatic(void *context, otMessage *msg, const otMessageInfo *info) {
        static_cast<ThreadNode*>(context)->onCoapTempRequest(msg, info);
    }

    void onStateChanged(otChangedFlags flags) {
        if (flags & OT_CHANGED_THREAD_ROLE) {
            otDeviceRole r = otThreadGetDeviceRole(instance_);
            DeviceRole role = DeviceRole::Unknown;
            switch (r) {
            case OT_DEVICE_ROLE_DISABLED: role = DeviceRole::Disabled; break;
            case OT_DEVICE_ROLE_DETACHED: role_str = DeviceRole::Detached; break;
            case OT_DEVICE_ROLE_CHILD:    role = DeviceRole::Child; break;
            case OT_DEVICE_ROLE_ROUTER:   role = DeviceRole::Router; break;
            case OT_DEVICE_ROLE_LEADER:   role = DeviceRole::Leader; break;
            }
            std::cout << "[C++ Thread] Зміна ролі -> " << static_cast<int>(role) << std::endl;
        }
    }

    void onUdpReceive(otMessage *message, const otMessageInfo *messageInfo) {
        char buf[128];
        uint16_t len = otMessageGetLength(message) - otMessageGetOffset(message);
        len = std::min<uint16_t>(len, sizeof(buf) - 1);

        otMessageRead(message, otMessageGetOffset(message), buf, len);
        buf[len] = '\0';

        char ipStr[OT_IP6_ADDRESS_STRING_SIZE];
        otIp6AddressToString(&messageInfo->mPeerAddr, ipStr, sizeof(ipStr));

        std::cout << "[C++ UDP Rx] Від [" << ipStr << "]:" << messageInfo->mPeerPort << " -> " << buf << std::endl;
    }

    void onCoapTempRequest(otMessage *message, const otMessageInfo *messageInfo) {
        if (otCoapMessageGetCode(message) == OT_COAP_CODE_GET) {
            otMessage *response = otCoapNewMessage(instance_, nullptr);
            if (!response) return;

            otCoapMessageInitResponse(response, message, OT_COAP_TYPE_ACKNOWLEDGMENT, OT_COAP_CODE_CONTENT);
            otCoapMessageSetFormat(response, OT_COAP_OPTION_CONTENT_FORMAT_TEXT_PLAIN);

            constexpr std::string_view payload = "{\"temp\": 23.5, \"unit\": \"C\"}";
            otCoapMessageSetPayloadMarker(response);
            otMessageAppend(response, payload.data(), static_cast<uint16_t>(payload.size()));

            otCoapSendResponse(instance_, response, messageInfo);
            std::cout << "[C++ CoAP] Відправлено відповідь на GET /sensors/temp" << std::endl;
        }
    }

    otInstance *instance_{nullptr};
    otUdpSocket socket_{};
    otCoapResource tempResource_{};
    bool socketOpened_{false};
    bool coapStarted_{false};
};

} // namespace thread_mesh

int main() {
    using namespace thread_mesh;
    try {
        ThreadNode node;
        constexpr std::array<uint8_t, 16> netKey = {
            0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,
            0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff
        };

        node.configureNetwork(15, 0x1234, netKey, "Thread-OpenLab");
        node.start();
        node.openUdpPort(12345);
        node.enableCoapService();

        std::cout << "Вузол Thread ініціалізовано. Очікування входження в мережу..." << std::endl;

        while (true) {
            node.processTasks();
            if (!node.hasPendingTasks()) {
                /* Очікування наступної системної події */
            }
        }
    } catch (const std::exception& e) {
        std::cerr << "Фатальна помилка: " << e.what() << std::endl;
        return -1;
    }
    return 0;
}
```
:::

---

### Детальний аналіз архітектурних механізмів стеку

#### 1. Робота з протоколом CoAP та сервісна модель даних
Хоча сирі UDP-сокети забезпечують мінімальні накладні витрати на передачу байтів, реальні комерційні IoT-системи та екосистеми Matter/Thread використовують прикладний протокол **CoAP** (*Constrained Application Protocol*, RFC 7252). CoAP забезпечує парадигму RESTful API поверх легковажного транспорту UDP:
* **Модель ресурсів:** кожен сенсор або актуатор ідентифікується уніфікованим шляхом URI (наприклад `/sensors/temp`, `/lights/living_room/state`).
* **Типи повідомлень:** `Confirmable` (CON — потребує негайного підтвердження ACK або повторюється з експоненційною затримкою) та `Non-Confirmable` (NON — регулярна телеметрія без підтвердження).
* **Стиснення кодів стану та заголовків:** замість довгих текстових рядків HTTP (`200 OK`, `404 Not Found`) CoAP використовує 1-байтні числові коди (`2.05 Content`, `4.04 Not Found`) та компактні числові опції бінарного формату TLV (Option Delta).
* **Механізм Observe (RFC 7641):** клієнт (наприклад прикордонний маршрутизатор) надсилає один запит `GET /sensors/temp` зі спеціальним прапорцем `Observe`. Сенсор реєструє підписку і самостійно надсилає оновлення лише тоді, коли виміряна температура змінюється більше ніж на заданий поріг. Це повністю усуває необхідність постійного опитування датчика із зовнішньої мережі.

У наведеному вище коді функція `otCoapAddResource` реєструє відповідний маршрут у внутрішньому дереві OpenThread. Коли з мережі надходить запит на порт `5683`, стек розбирає заголовки CoAP і викликає зареєстрований обробник `handle_coap_temp_request`, передаючи йому готовий контекст та дескриптор вхідного повідомлення.

#### 2. Модель пам'яті та життєвий цикл дескрипторів `otMessage`
Однією з найпідступніших пасток при роботі з низькорівневим C API OpenThread є нерозуміння правил передачі володіння буферами повідомлень. Стек не використовує загальносистемний куповий розподілювач `malloc`/`free`, оскільки динамічна фрагментація пам'яті неприпустима в надійних IoT-системах реального часу. Натомість OpenThread оперує статичним пулом фіксованих блоків (Buffer Pool), з яких конструюються повідомлення змінного розміру.

Коли прикладний код викликає `otUdpNewMessage()` або `otCoapNewMessage()`, виділяється заголовок повідомлення та перший блок пам'яті. Функція `otMessageAppend()` дописує корисні байти даних, автоматично зв'язуючи додаткові блоки пулу за потреби. Якщо формування повідомлення завершилося успішно, програма викликає `otUdpSend()` або `otCoapSendResponse()`. 

Тут діє строге правило передачі володіння:
* Якщо функція відправки повернула `OT_ERROR_NONE`, відповідальність за визволення пам'яті **повністю переходить до внутрішнього планувальника OpenThread**. Стек самостійно фрагментує датаграму на рівні 6LoWPAN, відправить кадри канального рівня, дочекається підтверджень MAC ACK і поверне блоки в пул. Повторний виклик `otMessageFree()` у прикладному коді спричинить подвійне звільнення пам'яті (Double Free) та аварійний збій мікроконтролера.
* Якщо ж функція повернула код помилки (наприклад `OT_ERROR_NO_BUFS` через переповнення черги передавача чи `OT_ERROR_INVALID_ARGS`), володіння **залишається за прикладним кодом**. Розробник зобов'язаний негайно викликати `otMessageFree(msg)`, інакше буфери пулу вичерпаються за лічені секунди активної роботи, заблокувавши роботу всього мережевого стеку.

У реалізації C++ ця небезпека повністю нейтралізується використанням типу `std::expected` та суворої інкапсуляції всередині методу `sendUdp()`, який гарантує коректне очищення дескриптора при будь-яких кодах помилок.

#### 3. Асинхронний диспетчер подій та кооперативні тасклети
OpenThread спроєктовано за безблокувальною моделлю. Жодна функція стеку (ні `otUdpSend`, ні `otDatasetSetActive`, ні операції шифрування AES) не блокує виконання процесора в очікуванні відповіді з ефіру. Замість цього всі системні події (завершення передачі кадру, спрацьовування таймера MLE, надходження радіопакета) додають легкорозмірні задачі — тасклети (Tasklets) — у пріоритетну кільцеву чергу.

Головний цикл програми зобов'язаний регулярно викликати `otTaskletsProcess(instance)`. Ця функція виконує всі накопичені мережеві операції по черзі. Якщо функція `otTaskletsArePending(instance)` повертає `false`, це означає, що всі поточні мережеві задачі виконано, і мікроконтролер може безпечно перейти в режим енергозбереження з низьким споживанням струму (`__WFI()` — Wait For Interrupt у середовищі ARM Cortex-M) доти, доки апаратне переривання від таймера чи радіотрансивера не розбудить ядро. Крім того, у промислових виробах у головному циклі обов'язково скидається апаратний сторожовий таймер (Hardware Watchdog Timer, WDT) з інтервалом 5–10 секунд. Якщо зависання блокуючої функції завадить черговому скиданню WDT, мікроконтролер виконає повне апаратне перезавантаження та автоматично відновить з'єднання з мережею з енергонезалежної пам'яті.

> [!WARNING]
> Будь-які довгі блокуючі виклики (наприклад `delay_ms(500)`) усередині головного циклу чи в тілі функцій зворотного виклику (`handle_state_changed`, `handle_udp_receive`) категорично неприпустимі. Затримка обробки тасклетів призведе до пропуску часових вікон MAC ACK, зриву таймерів очікування MLE та розриву зв'язку з батьківським маршрутизатором.

#### 4. Динамічне комісіонування через Joiner API (ECJPAKE)
У серійному виробництві пристроїв записувати фіксований майстер-ключ у прошивку заборонено вимогами безпеки. Замість виклику `otDatasetSetActive` вузол запускається в режимі **Joiner**, знаючи лише унікальний заводський пароль (PSKd):

:::tabs
```c
static void handle_joiner_callback(otError error, void *context)
{
    if (error == OT_ERROR_NONE) {
        printf("[Joiner] Комісіонування успішне! Запуск Thread...\n");
        otThreadSetEnabled((otInstance *)context, true);
    } else {
        printf("[Joiner Помилка] Код: %d\n", error);
    }
}

void start_secure_commissioning(otInstance *instance, const char *pskd)
{
    /* Запуск DTLS-рукостискання ECJPAKE через найближчий Joiner Router */
    otJoinerStart(instance, pskd, NULL, "VendorLab", "TempSensor", "v1.0", NULL, 
                  handle_joiner_callback, instance);
}
```
```cpp
void startSecureCommissioning(otInstance *instance, std::string_view pskd)
{
    auto callback = [](otError error, void *ctx) {
        if (error == OT_ERROR_NONE) {
            std::cout << "[Joiner] Комісіонування успішне! Запуск Thread..." << std::endl;
            otThreadSetEnabled(static_cast<otInstance*>(ctx), true);
        } else {
            std::cerr << "[Joiner Помилка] Код: " << error << std::endl;
        }
    };

    otJoinerStart(instance, pskd.data(), nullptr, "VendorLab", "TempSensor", "v1.0", nullptr,
                  callback, instance);
}
```
:::
*Типові коди помилок комісіонування:*
* `OT_ERROR_NOT_FOUND` — жоден сусідній маршрутизатор не перебуває у режимі Joiner Router і не транслює пакети Discovery Response.
* `OT_ERROR_SECURITY` — введений користувачем пароль PSKd не збігається з паролем на пристрої, протокол ECJPAKE перервано через помилку автентифікації.
* `OT_ERROR_RESPONSE_TIMEOUT` — прикордонний маршрутизатор або смартфон комісіонера не встиг надіслати підтвердження у відведений інтервал часу.

#### 5. Розрахунок енергоспоживання для сплячих пристроїв (SED та SSED)
Для сенсорів на літієвих батареях (CR2032 ємністю 220 мА·год) режим роботи радіомодуля є визначальним фактором тривалості життя:

* **Постійно увімкнений прийом (Router / FED / MED):**
  * Струм прийому `I_rx ≈ 6.5 мА`.
  * Час роботи:
  ```
  T = 220 мА·год / 6.5 мА ≈ 33.8 години
  ```
  Пристрій повністю вичерпає ємність батареї менш ніж за півтори доби.
* **Сплячий вузол SED із класичним опитуванням (Indirect Polling, інтервал 3 секунди):**
  * Струм глибокого сну мікроконтролера: `I_sleep ≈ 1.5 мкА`.
  * Кожні 3 секунди вузол прокидається на 2.5 мс для надсилання MAC Data Request: струм імпульсу `I_poll ≈ 12 мА`.
  * Середній струм:
  ```
  I_avg = I_sleep + (I_poll · t_poll) / T_interval
  = 0.0015 мА + (12 мА · 0.0025 с) / 3 с
  = 0.0015 мА + 0.0100 мА = 0.0115 мА (11.5 мкА)
  ```
  * Час автономної роботи:
  ```
  T = 220 мА·год / 0.0115 мА ≈ 19130 годин ≈ 2.18 року
  ```
* **Синхронізований вузол SSED із механізмом CSL (Thread 1.2+, вікно вибірки 500 мс):**
  * Вузол не відправляє кадри опитування, а лише вмикає приймач на 160 мкс кожні 500 мс.
  * Середній струм знижується до 3.8 мкА, що забезпечує **понад 6.5 років безперервної роботи** від одного дискового елемента.

#### 6. Мультикаст-групи IPv6 та групове керування
Вузли Thread автоматично приєднуються до стандартизованих мультикаст-груп IPv6 для отримання загальномережевих сповіщень:
* `ff02::1` — усі вузли на відстані одного радіострибка (Link-Local All-Nodes).
* `ff03::1` — усі пристрої в межах даного сегмента Thread (Realm-Local All-Thread-Nodes).
* `ff03::2` — усі активні маршрутизатори в сегменті (Realm-Local All-Thread-Routers).

Для отримання кастомних групових повідомлень (наприклад керування всіма світильниками в групі) додаток використовує API підписки:

:::tabs
```c
void subscribe_light_group(otInstance *instance)
{
    otNetifMulticastAddress mc_addr;
    memset(&mc_addr, 0, sizeof(mc_addr));
    otIp6AddressFromString("ff03::beef:1", &mc_addr.mAddress);

    otIp6SubscribeMulticastAddress(instance, &mc_addr);
    printf("[IPv6] Підписано на мультикаст ff03::beef:1\n");
}
```
```cpp
void subscribeLightGroup(otInstance *instance, std::string_view multicastIp)
{
    otNetifMulticastAddress mcAddr{};
    otIp6AddressFromString(multicastIp.data(), &mcAddr.mAddress);

    otIp6SubscribeMulticastAddress(instance, &mcAddr);
    std::cout << "[IPv6] Підписано на мультикаст " << multicastIp << std::endl;
}
```
:::

#### 7. Взаємодія з апаратним рівнем через `otPlatRadio` та діагностика Wireshark
Рівень абстракції платформи OpenThread комунікує з кремнієвим трансивером IEEE 802.15.4 через набір низькорівневих драйверних функцій:
* `otPlatRadioTransmit(instance, frame)` — передача сформованого кадру з автоматичним виконанням алгоритму CSMA/CA (Clear Channel Assessment). Радіотракт слухає ефір протягом 8 періодів символів (128 мкс), перевіряючи, щоб рівень енергії в каналі був нижче порога -75 дБм.
* `otPlatRadioReceiveDone(instance, frame, error)` — апаратне переривання по завершенню прийому кадру з перевіркою 16-бітної контрольної суми CRC (FCS).
* **Апаратна фільтрація адрес:** щоб центральне ядро ARM не прокидалося на сторонній радіотрафік сусідніх мереж, чіп радіотрансивера на апаратному рівні відкидає кадри, якщо поле `Destination PAN ID` або адреса одержувача не збігаються з локальними реєстрами пристрою.

Для діагностичного захоплення пакетів в ефірі розробники використовують USB-адаптер (наприклад nRF52840 Dongle) із прошивкою sniffer. Захоплений трафік передається через віртуальний COM-порт безпосередньо в програму **Wireshark**. Щоб Wireshark зміг розшифрувати кадри AES-128 CCM та стиснені заголовки 6LoWPAN IPHC, у налаштуваннях протоколу IEEE 802.15.4 вказується 128-бітний ключ:

```text
Edit -> Preferences -> Protocols -> IEEE 802.15.4 -> Decryption Keys:
Key: 00112233445566778899aabbccddeeff
Decryption Type: Thread Master Key
```
Після введення ключа Wireshark повністю розгортає дерево протоколів: від фізичних символів DSSS до прикладних запитів CoAP та структур даних Matter.

#### 8. Оновлення прошивки повітрям (FOTA over CoAP Block-Wise Transfer)
Оновлення мікропрограмного забезпечення автономних вузлів у великих mesh-мережах вимагає передачі бінарного файлу розміром від 200 до 600 КБ крізь вузькі канали IEEE 802.15.4. Оскільки розмір одного кадру обмежений 127 байтами, застосовується стандартизований механізм передачі блоками **CoAP Block-Wise Transfer** (RFC 7959):

```
Клієнт (Вузол FOTA)                                Сервер оновлень (OTBR)
       │                                                     │
       │ 1. GET /firmware/v2.bin (Block2: 0/0/128)          │
       ├────────────────────────────────────────────────────>│
       │                                                     │
       │ 2. 2.05 Content (Block2: 0/1/128, 128 Б даних)      │
       │<────────────────────────────────────────────────────┤
       │                                                     │
       │ 3. GET /firmware/v2.bin (Block2: 1/0/128)          │
       ├────────────────────────────────────────────────────>│
       │                                                     │
       │ 4. 2.05 Content (Block2: 1/1/128, 128 Б даних)      │
       │<────────────────────────────────────────────────────┤
       │ ... (Повторення для всіх N блоків)                 │
       │                                                     │
       │ N. GET /firmware/v2.bin (Block2: K/0/128)           │
       ├────────────────────────────────────────────────────>│
       │                                                     │
       │ N+1. 2.05 Content (Block2: K/0/128, Останній блок)  │
       │<────────────────────────────────────────────────────┤
       ▼                                                     ▼
```

Опція `Block2` у заголовку CoAP кодує три критичні параметри:
1. **Номер блоку (Block Number):** порядковий індекс фрагмента (0, 1, 2, ...).
2. **Прапорець продовження (More Flag, `M`):** `1` — у сервері є ще дані, `0` — це останній блок файлу.
3. **Розмір блоку (Size Exponent, `SZX`):** ступінь двійки від 16 до 1024 байтів (для Thread оптимальним є розмір 128 або 256 байтів, що запобігає зайвій фрагментації 6LoWPAN).

Вузол записує кожен отриманий блок у вторинний розділ зовнішньої Flash-пам'яті (Slot 1). Після отримання останнього блоку з прапорцем `M = 0` мікроконтролер обчислює хеш SHA-256 усього записаного образу та перевіряє асиметричний цифровий підпис ECDSA SECP256R1 відкритим ключем виробника, вшитим у завантажувач MCUboot. Якщо підпис валідний, виставляється прапорець готовності до перезавантаження, завантажувач копіює новий образ у робочу область пам'яті (Slot 0) і здійснює старт нової версії мікропрограми.

#### 9. Стійкість до завад Wi-Fi та динамічний вибір каналів (Energy Scan)
Діапазон 2.4 ГГц ISM є надзвичайно завантаженим. Стандартні точки доступу Wi-Fi 802.11b/g/n/ax використовують широкі смуги 20 МГц або 40 МГц із високою потужністю випромінювання (до 100–500 мВт), що легко глушить низькопотужні сигнали Thread (потужність передавача типово становить лише 0–8 дБм / 1–6 мВт).

```
Частота (ГГц)  2.412         2.437         2.462         2.480
Wi-Fi (20 МГц) [ Wi-Fi Канал 1 ]  [ Wi-Fi Канал 6 ]  [ Wi-Fi Канал 11 ]
Thread (5 МГц) 11 12 13 14 (15) 16 17 18 19 (20) 21 22 23 24 (25)(26)
```

Канали Thread 11–14 перекриваються Wi-Fi каналом 1, канали 16–19 — Wi-Fi каналом 6, а канали 21–24 — Wi-Fi каналом 11. Найбільш завадостійкими та безпечними для розгортання мереж Thread є так звані «міжканальні вікна» — канали **15, 20, 25 та 26**, які розташовані у проміжках між основними спектральними пелюстками Wi-Fi.

Під час формування нової мережі або відновлення після тривалої втрати зв'язку вузол викликає функцію `otLinkEnergyScan()`. Стек по черзі перемикає радіоприймач на кожен із 16 каналів, вимірює рівень фонового шуму протягом 100 мс і формує гістограму завантаженості ефіру. Leader обирає канал із найнижчим середнім рівнем завад (типово нижче -85 дБм).

#### 10. Діагностичні лічильники мережі та адаптивне регулювання потужності
Для автоматизованого моніторингу працездатності великих промислових інсталяцій OpenThread надає вбудовані засоби збору апаратної статистики через модуль Network Diagnostics. Кожен маршрутизатор і кінцевий вузол веде внутрішні лічильники:
* **MAC Tx Success Count та MAC Tx Failure Count:** співвідношення успішних передач до кількості втрачених пакетів через відсутність кадру MAC ACK. Якщо коефіцієнт помилок перевищує 15%, вузол сигналізує про деградацію радіолінку.
* **MAC CCA Failure Count:** лічильник ситуацій, коли радіотрансивер скасував спробу передачі через зайнятість ефіру стороннім сигналом під час процедури CSMA/CA. Високе значення цього лічильника вказує на наявність поруч активної точки доступу Wi-Fi чи мікрохвильової печі.
* **MAC Retry Count:** середня кількість повторних спроб передачі кадру перед успішною доставкою.

На основі цих метрик вузли можуть виконувати динамічне регулювання вихідної потужності передавача через виклик `otPlatRadioSetTransmitPower()`. У приміщеннях із високою щільністю вузлів потужність знижується з +8 дБм до 0 дБм або -4 дБм. Це суттєво зменшує взаємну радіоінтерференцію між сусідніми кімнатами, знижує струм споживання мікроконтролера під час передачі з 15 мА до 5–7 мА і значно підвищує загальну пропускну здатність mesh-мережі за рахунок просторового повторного використання каналів. Крім того, стек OpenThread дозволяє динамічно налаштовувати поріг чутливості прийому (CCA Energy Detect Threshold) через конфігураційний параметр `OPENTHREAD_CONFIG_RADIO_DEFAULT_RSSI_CORRECTION`. Це забезпечує точне калібрування радіотракту під специфічні узгоджувальні ланцюги друкованих антен та коаксіальних роз'ємів SMA на користувацьких платах.

#### 11. Практичне тестування через POSIX-емуляцію
Для швидкого налагодження вузлів Thread без фізичного обладнання OpenThread надає віртуальний радіодрайвер POSIX:

```bash
# Термінал 1: Запуск першого вузла (створення мережі як Leader)
$ ./ot-cli-ftd 1
> dataset init new
> dataset commit active
> ifconfig up
> thread start
> state
leader
> ipaddr mleid
fdde:ad00:beef:0:166e:a00:0:1

# Термінал 2: Запуск другого вузла (підключення як Child/Router)
$ ./ot-cli-ftd 2
> dataset set active <шістнадцятковий_дамп_з_вузла_1>
> ifconfig up
> thread start
> state
child
> udp open
> udp bind :: 12345
> udp send fdde:ad00:beef:0:166e:a00:0:1 12345 "Привіт від вузла 2!"
```
У терміналі першого вузла негайно відобразиться прийняте UDP-повідомлення, підтверджуючи безперешкодне проходження трафіку крізь рівні 6LoWPAN та IEEE 802.15.4 віртуального радіоефіру.
