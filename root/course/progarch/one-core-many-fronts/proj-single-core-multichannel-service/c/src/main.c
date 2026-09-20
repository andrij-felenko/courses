#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <stdbool.h>

#include "climate_core.h"
#include "cli_adapter.h"
#include "http_adapter.h"
#include "queue_adapter.h"

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#define close_socket(s) closesocket((SOCKET)(s))
#else
#include <unistd.h>
#include <sys/socket.h>
#define close_socket(s) close(s)
#endif

/**
 * @file main.c
 * @brief Корінь композиції (Composition Root) та демонстраційний стенд.
 *
 * Інстанціює єдине прикладне ядро, зв'язує його вхідний порт з трьома драйвуючими
 * адаптерами (CLI, HTTP, Queue) та верифікує ідентичність бізнес-поведінки.
 */

#define TEST_AUTH_TOKEN "secret-token-pass-2026"

/**
 * @brief Допоміжна функція створення пари з'єднаних сокетів для тестів I/O.
 */
static int create_connected_socket_pair(int sv[2]) {
#ifdef _WIN32
    SOCKET listener = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (listener == INVALID_SOCKET) return -1;

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = 0;

    if (bind(listener, (struct sockaddr *)&addr, sizeof(addr)) == SOCKET_ERROR) {
        closesocket(listener);
        return -1;
    }
    int len = sizeof(addr);
    if (getsockname(listener, (struct sockaddr *)&addr, &len) == SOCKET_ERROR) {
        closesocket(listener);
        return -1;
    }
    if (listen(listener, 1) == SOCKET_ERROR) {
        closesocket(listener);
        return -1;
    }

    SOCKET client = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (client == INVALID_SOCKET) {
        closesocket(listener);
        return -1;
    }
    if (connect(client, (struct sockaddr *)&addr, sizeof(addr)) == SOCKET_ERROR) {
        closesocket(listener);
        closesocket(client);
        return -1;
    }

    SOCKET server = accept(listener, NULL, NULL);
    closesocket(listener);
    if (server == INVALID_SOCKET) {
        closesocket(client);
        return -1;
    }

    sv[0] = (int)client;
    sv[1] = (int)server;
    return 0;
#else
    return socketpair(AF_UNIX, SOCK_STREAM, 0, sv);
#endif
}

/**
 * @brief Демонстрація Сценарію 1: Консольний фронт (CLI Driving Adapter).
 */
static void demo_cli_adapter(inbound_port_t *port) {
    printf("\n====================================================================\n");
    printf("  СЦЕНАРІЙ 1: Консольний адаптер (CLI Driving Adapter)\n");
    printf("====================================================================\n");

    /* 1. Успішне встановлення цільової температури у вітальні */
    char *argv_ok[] = {
        "climate-cli",
        "--room", "living-room",
        "--temp", "22.5",
        "--token", TEST_AUTH_TOKEN
    };
    int exit_code = cli_adapter_run(port, 7, argv_ok);
    assert(exit_code == CLI_EXIT_SUCCESS);
    printf("  -> Результат: код %d [OK]\n", exit_code);

    /* 2. Помилка автентифікації клієнта */
    char *argv_unauth[] = {
        "climate-cli",
        "--room", "living-room",
        "--temp", "23.0",
        "--token", "invalid-token"
    };
    exit_code = cli_adapter_run(port, 7, argv_unauth);
    assert(exit_code == CLI_EXIT_UNAUTHORIZED);
    printf("  -> Результат: код %d [Очікуване відхилення авторизації]\n", exit_code);

    /* 3. Порушення бізнес-правила діапазону температур */
    char *argv_out_of_range[] = {
        "climate-cli",
        "--room", "living-room",
        "--temp", "38.5",
        "--token", TEST_AUTH_TOKEN
    };
    exit_code = cli_adapter_run(port, 7, argv_out_of_range);
    assert(exit_code == CLI_EXIT_OUT_OF_RANGE);
    printf("  -> Результат: код %d [Очікуване відхилення діапазону]\n", exit_code);

    /* 4. Помилка синтаксису параметрів командного рядка */
    char *argv_syntax_err[] = {
        "climate-cli",
        "--unknown-flag", "value"
    };
    exit_code = cli_adapter_run(port, 3, argv_syntax_err);
    assert(exit_code == CLI_EXIT_INVALID_SYNTAX);
    printf("  -> Результат: код %d [Очікувана синтаксична помилка]\n", exit_code);
}

/**
 * @brief Демонстрація Сценарію 2: Мережевий HTTP-фронт (HTTP Driving Adapter).
 */
static void demo_http_adapter(inbound_port_t *port) {
    printf("\n====================================================================\n");
    printf("  СЦЕНАРІЙ 2: Мережевий HTTP-адаптер (HTTP Driving Adapter)\n");
    printf("====================================================================\n");

    int sv[2];
    char resp_buf[1024];

    /* 1. Успішний запит (POST 200 OK) для кімнати 'kitchen' */
    assert(create_connected_socket_pair(sv) == 0);
    const char *http_req_ok =
        "POST /api/climate HTTP/1.1\r\n"
        "Host: localhost\r\n"
        "Authorization: Bearer " TEST_AUTH_TOKEN "\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: 33\r\n"
        "\r\n"
        "{\"room\":\"kitchen\",\"temp\":19.5}";

#ifdef _WIN32
    send((SOCKET)sv[0], http_req_ok, (int)strlen(http_req_ok), 0);
#else
    send(sv[0], http_req_ok, strlen(http_req_ok), 0);
#endif

    int handle_res = http_adapter_handle_fd(port, sv[1]);
    assert(handle_res == 0);

#ifdef _WIN32
    int r = recv((SOCKET)sv[0], resp_buf, sizeof(resp_buf) - 1, 0);
#else
    ssize_t r = recv(sv[0], resp_buf, sizeof(resp_buf) - 1, 0);
#endif
    assert(r > 0);
    resp_buf[r] = '\0';
    assert(strstr(resp_buf, "HTTP/1.1 200 OK") != NULL);
    printf("  [HTTP 200 OK] Успішна зміна мікроклімату кухні:\n%s\n", resp_buf);

    close_socket(sv[0]);
    close_socket(sv[1]);

    /* 2. Запит із недійсним токеном (POST 401 Unauthorized) */
    assert(create_connected_socket_pair(sv) == 0);
    const char *http_req_unauth =
        "POST /api/climate HTTP/1.1\r\n"
        "Authorization: Bearer bad-token\r\n"
        "\r\n"
        "{\"room\":\"kitchen\",\"temp\":20.0}";

#ifdef _WIN32
    send((SOCKET)sv[0], http_req_unauth, (int)strlen(http_req_unauth), 0);
#else
    send(sv[0], http_req_unauth, strlen(http_req_unauth), 0);
#endif

    handle_res = http_adapter_handle_fd(port, sv[1]);
    assert(handle_res == 0);

#ifdef _WIN32
    r = recv((SOCKET)sv[0], resp_buf, sizeof(resp_buf) - 1, 0);
#else
    r = recv(sv[0], resp_buf, sizeof(resp_buf) - 1, 0);
#endif
    assert(r > 0);
    resp_buf[r] = '\0';
    assert(strstr(resp_buf, "HTTP/1.1 401 Unauthorized") != NULL);
    printf("  [HTTP 401 Unauthorized] Відмова авторизації підтверджена [OK]\n");

    close_socket(sv[0]);
    close_socket(sv[1]);

    /* 3. Запит із неприпустимою температурою (POST 422 Unprocessable Entity) */
    assert(create_connected_socket_pair(sv) == 0);
    const char *http_req_out_of_range =
        "POST /api/climate HTTP/1.1\r\n"
        "Authorization: Bearer " TEST_AUTH_TOKEN "\r\n"
        "\r\n"
        "{\"room\":\"kitchen\",\"temp\":10.0}";

#ifdef _WIN32
    send((SOCKET)sv[0], http_req_out_of_range, (int)strlen(http_req_out_of_range), 0);
#else
    send(sv[0], http_req_out_of_range, strlen(http_req_out_of_range), 0);
#endif

    handle_res = http_adapter_handle_fd(port, sv[1]);
    assert(handle_res == 0);

#ifdef _WIN32
    r = recv((SOCKET)sv[0], resp_buf, sizeof(resp_buf) - 1, 0);
#else
    r = recv(sv[0], resp_buf, sizeof(resp_buf) - 1, 0);
#endif
    assert(r > 0);
    resp_buf[r] = '\0';
    assert(strstr(resp_buf, "HTTP/1.1 422 Unprocessable Entity") != NULL);
    printf("  [HTTP 422 Unprocessable Entity] Валідація діапазону температури підтверджена [OK]\n");

    close_socket(sv[0]);
    close_socket(sv[1]);
}

/**
 * @brief Демонстрація Сценарію 3: Асинхронний фронт черги (Queue Driving Adapter).
 */
static void demo_queue_adapter(inbound_port_t *port) {
    printf("\n====================================================================\n");
    printf("  СЦЕНАРІЙ 3: Асинхронна черга повідомлень (Queue Driving Adapter)\n");
    printf("====================================================================\n");

    int qv[2];

    /* 1. Успішне повідомлення для кімнати 'bedroom' -> ACK */
    assert(create_connected_socket_pair(qv) == 0);
    queue_message_envelope_t msg_ok;
    memset(&msg_ok, 0, sizeof(msg_ok));
    strncpy(msg_ok.message_id, "msg-uuid-001", sizeof(msg_ok.message_id) - 1);
    strncpy(msg_ok.correlation_id, "trace-abc-123", sizeof(msg_ok.correlation_id) - 1);
    msg_ok.delivery_attempt = 1;
    msg_ok.timestamp_ms = 1773560000000ULL;
    strncpy(msg_ok.auth_token, TEST_AUTH_TOKEN, sizeof(msg_ok.auth_token) - 1);
    strncpy(msg_ok.room_id, "bedroom", sizeof(msg_ok.room_id) - 1);
    msg_ok.target_temp_c = 24.0;

#ifdef _WIN32
    send((SOCKET)qv[0], (const char *)&msg_ok, (int)sizeof(msg_ok), 0);
#else
    write(qv[0], &msg_ok, sizeof(msg_ok));
#endif

    queue_action_t action = queue_adapter_poll_fd(port, qv[1], 100);
    assert(action == QUEUE_ACTION_ACK);
    printf("  -> Директива брокеру: %s [OK]\n", queue_action_to_string(action));

    close_socket(qv[0]);
    close_socket(qv[1]);

    /* 2. Отруйне повідомлення з неприпустимою температурою 45.0 C -> DLQ */
    assert(create_connected_socket_pair(qv) == 0);
    queue_message_envelope_t msg_poison;
    memset(&msg_poison, 0, sizeof(msg_poison));
    strncpy(msg_poison.message_id, "msg-uuid-poison", sizeof(msg_poison.message_id) - 1);
    msg_poison.delivery_attempt = 3;
    strncpy(msg_poison.auth_token, TEST_AUTH_TOKEN, sizeof(msg_poison.auth_token) - 1);
    strncpy(msg_poison.room_id, "bedroom", sizeof(msg_poison.room_id) - 1);
    msg_poison.target_temp_c = 45.0;

#ifdef _WIN32
    send((SOCKET)qv[0], (const char *)&msg_poison, (int)sizeof(msg_poison), 0);
#else
    write(qv[0], &msg_poison, sizeof(msg_poison));
#endif

    action = queue_adapter_poll_fd(port, qv[1], 100);
    assert(action == QUEUE_ACTION_DLQ);
    printf("  -> Директива брокеру: %s (ізоляція фатальної бізнес-помилки) [OK]\n", queue_action_to_string(action));

    close_socket(qv[0]);
    close_socket(qv[1]);

    /* 3. Симуляція порожньої черги (таймаут poll) */
    assert(create_connected_socket_pair(qv) == 0);
    action = queue_adapter_poll_fd(port, qv[1], 10);
    assert(action == QUEUE_ACTION_TIMEOUT);
    printf("  -> Директива брокеру: %s (черга очікує нових повідомлень) [OK]\n", queue_action_to_string(action));

    close_socket(qv[0]);
    close_socket(qv[1]);
}

int main(void) {
#ifdef _WIN32
    WSADATA wsa;
    WSAStartup(MAKEWORD(2, 2), &wsa);
#endif

    printf("====================================================================\n");
    printf("  Архітектура 'Порти й Адаптери': Одне ядро, кілька фронтів\n");
    printf("====================================================================\n");

    /* 1. Ініціалізація єдиного доменного ядра мікроклімату */
    climate_core_t core;
    climate_core_init(&core, TEST_AUTH_TOKEN);

    /* 2. Отримання нейтрального контракту вхідного порту */
    inbound_port_t *port = climate_core_get_port(&core);
    assert(port != NULL);

    /* 3. Послідовна демонстрація симетричного виконання на трьох фронтах */
    demo_cli_adapter(port);
    demo_http_adapter(port);
    demo_queue_adapter(port);

    /* 4. Фінальна верифікація єдиного стану ядра */
    printf("\n====================================================================\n");
    printf("  ФІНАЛЬНА ВЕРИФІКАЦІЯ СТАНУ ЯДРА (Domain State Invariants)\n");
    printf("====================================================================\n");

    double t_living = 0.0, t_kitchen = 0.0, t_bedroom = 0.0;
    assert(climate_core_get_room_temp(&core, "living-room", &t_living));
    assert(climate_core_get_room_temp(&core, "kitchen", &t_kitchen));
    assert(climate_core_get_room_temp(&core, "bedroom", &t_bedroom));

    printf("  - 'living-room' (встановлено через CLI):   %.1f C [Очікувалось: 22.5 C]\n", t_living);
    printf("  - 'kitchen'     (встановлено через HTTP):  %.1f C [Очікувалось: 19.5 C]\n", t_kitchen);
    printf("  - 'bedroom'     (встановлено через Queue): %.1f C [Очікувалось: 24.0 C]\n", t_bedroom);

    assert(t_living == 22.5);
    assert(t_kitchen == 19.5);
    assert(t_bedroom == 24.0);

    printf("\n  [УСПІХ] Усі бізнес-правила виконані симетрично без дублювання логіки!\n");
    printf("====================================================================\n");

#ifdef _WIN32
    WSACleanup();
#endif

    return 0;
}
