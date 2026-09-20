#include "queue_adapter.h"
#include <stdio.h>
#include <string.h>

#ifdef _WIN32
#include <winsock2.h>
#define poll WSAPoll
#define queue_read(fd, buf, len) recv((SOCKET)(fd), (char *)(buf), (int)(len), 0)
#else
#include <poll.h>
#include <unistd.h>
#define queue_read(fd, buf, len) read(fd, buf, len)
#endif

/**
 * @file queue_adapter.c
 * @brief Реалізація драйвуючого асинхронного адаптера черги через poll().
 */

const char *queue_action_to_string(queue_action_t action) {
    switch (action) {
        case QUEUE_ACTION_ACK:
            return "ACK";
        case QUEUE_ACTION_NACK:
            return "NACK";
        case QUEUE_ACTION_DLQ:
            return "DLQ";
        case QUEUE_ACTION_TIMEOUT:
            return "TIMEOUT";
        case QUEUE_ACTION_ERROR:
            return "ERROR";
        default:
            return "UNKNOWN";
    }
}

queue_action_t queue_adapter_poll_fd(inbound_port_t *port, int queue_fd, int timeout_ms) {
    if (!port || queue_fd < 0) {
        return QUEUE_ACTION_ERROR;
    }

    /* 1. Моніторинг готовності дескриптора через системний виклик poll */
    struct pollfd pfd;
    pfd.fd = queue_fd;
    pfd.events = POLLIN;
    pfd.revents = 0;

    int poll_res = poll(&pfd, 1, timeout_ms);
    if (poll_res < 0) {
        fprintf(stderr, "[QUEUE] Системна помилка виклику poll()\n");
        return QUEUE_ACTION_ERROR;
    }
    if (poll_res == 0) {
        /* Черга порожня, таймаут очікування сплив */
        return QUEUE_ACTION_TIMEOUT;
    }
    if (!(pfd.revents & POLLIN)) {
        fprintf(stderr, "[QUEUE] Помилка або закриття дескриптора каналу черги (revents=0x%X)\n", pfd.revents);
        return QUEUE_ACTION_ERROR;
    }

    /* 2. Вичитування конверта повідомлення */
    queue_message_envelope_t envelope;
    memset(&envelope, 0, sizeof(envelope));

    ssize_t bytes_read = queue_read(queue_fd, &envelope, sizeof(envelope));
    if (bytes_read != (ssize_t)sizeof(envelope)) {
        /* Пакет фрагментований або пошкоджений (Poison Message) -> негайно в DLQ */
        fprintf(stderr, "[QUEUE] Отримано пошкоджений пакет (%zd з %zu байт) -> відправка в DLQ\n",
                bytes_read, sizeof(envelope));
        return QUEUE_ACTION_DLQ;
    }

    /* 3. Трансляція полів конверта в нейтральну команду вхідного порту */
    climate_cmd_t cmd;
    memset(&cmd, 0, sizeof(cmd));
    strncpy(cmd.room_id, envelope.room_id, sizeof(cmd.room_id) - 1);
    cmd.target_temp_c = envelope.target_temp_c;
    strncpy(cmd.auth_token, envelope.auth_token, sizeof(cmd.auth_token) - 1);

    climate_result_t result;
    memset(&result, 0, sizeof(result));

    core_status_t status = inbound_port_execute(port, &cmd, &result);

    /* 4. Мапінг доменних статусів ядра у протокольні директиви квитування */
    queue_action_t action;
    switch (status) {
        case CORE_STATUS_OK:
            action = QUEUE_ACTION_ACK;
            printf("[QUEUE] Повідомлення '%s' (спроба %u): %s -> [ACK]\n",
                   envelope.message_id, envelope.delivery_attempt, result.message);
            break;

        case CORE_STATUS_INTERNAL_ERROR:
            action = QUEUE_ACTION_NACK;
            printf("[QUEUE] Повідомлення '%s' (спроба %u): Тимчасовий збій системи (%s) -> [NACK: повтор]\n",
                   envelope.message_id, envelope.delivery_attempt, result.message);
            break;

        case CORE_STATUS_INVALID_ARG:
        case CORE_STATUS_UNAUTHORIZED:
        case CORE_STATUS_OUT_OF_RANGE:
        default:
            action = QUEUE_ACTION_DLQ;
            printf("[QUEUE] Повідомлення '%s' (спроба %u): Бізнес-помилка [%s] (%s) -> [DLQ: ізоляція]\n",
                   envelope.message_id, envelope.delivery_attempt, core_status_to_string(status), result.message);
            break;
    }

    return action;
}
