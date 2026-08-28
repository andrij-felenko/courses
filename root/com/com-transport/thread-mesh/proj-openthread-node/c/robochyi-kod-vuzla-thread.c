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
