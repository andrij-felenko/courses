#include "dns_server.h"

#include <errno.h>
#include <stdbool.h>
#include <string.h>

#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "dns";

#define DNS_PORT 53
#define DNS_TASK_STACK 3072
#define DNS_TASK_PRIO 5

/*
 * 512 байтів — історична межа DNS поверх UDP. Запит, що не вліз у неї,
 * клієнт повторює по TCP, а зонди операційних систем таких не шлють.
 * Буфер лежить на стеку завдання: купу не чіпаємо взагалі, тож потік
 * запитів від фонових служб телефона не фрагментує пам'ять.
 */
#define DNS_BUFFER_SIZE 512

#define DNS_HEADER_LEN 12   /* ID, прапорці й чотири лічильники секцій */
#define DNS_ANSWER_LEN 16   /* вказівник 2 + type 2 + class 2 + TTL 4 + len 2 + IPv4 4 */
#define DNS_TTL_SECONDS 10

#define DNS_TYPE_A 1
#define DNS_CLASS_IN 1

/* Зміщення полів заголовка. */
#define OFF_FLAGS_HI 2
#define OFF_FLAGS_LO 3
#define OFF_QDCOUNT 4
#define OFF_ANCOUNT 6
#define OFF_NSCOUNT 8
#define OFF_ARCOUNT 10

static TaskHandle_t s_task = NULL;
static volatile bool s_running = false;
static int s_sock = -1;
static uint32_t s_answer_ip = 0;

static inline uint16_t read_u16(const uint8_t *p)
{
    return (uint16_t)((p[0] << 8) | p[1]);
}

static inline void write_u16(uint8_t *p, uint16_t value)
{
    p[0] = (uint8_t)(value >> 8);
    p[1] = (uint8_t)(value & 0xFF);
}

/*
 * Знаходить, де закінчується секція питання: послідовність міток
 * «довжина + байти», нульова мітка, далі QTYPE і QCLASS.
 *
 * Дописувати відповідь наосліп у кінець отриманого пакета не можна:
 * Android і сучасні резолвери додають запис OPT (EDNS0) у секцію
 * додаткових, і відповідь, приліплена після нього, виходить зіпсованою.
 * Тому ми обрізаємо пакет саме тут, а лічильник ARCOUNT обнуляємо.
 */
static int question_section_end(const uint8_t *buf, int len)
{
    int off = DNS_HEADER_LEN;

    while (off < len) {
        const uint8_t label = buf[off];

        if (label == 0) {
            off += 1 + 4;   /* нульова мітка + QTYPE + QCLASS */
            return off <= len ? off : -1;
        }

        /* Стиснене посилання в секції питання неприпустиме за RFC 1035. */
        if ((label & 0xC0) != 0) {
            return -1;
        }

        off += 1 + label;
    }

    return -1;
}

/*
 * Перетворює запит на відповідь прямо в буфері й повертає її довжину,
 * або -1, якщо відповідати нема на що.
 */
static int build_response(uint8_t *buf, int len)
{
    if (len < DNS_HEADER_LEN) {
        return -1;
    }

    const uint16_t flags = read_u16(buf + OFF_FLAGS_HI);
    if (flags & 0x8000) {
        return -1;                      /* це вже відповідь, а не запит */
    }
    if (((flags >> 11) & 0x0F) != 0) {
        return -1;                      /* OPCODE != QUERY: не наша справа */
    }
    if (read_u16(buf + OFF_QDCOUNT) != 1) {
        return -1;
    }

    const int qend = question_section_end(buf, len);
    if (qend < 0) {
        return -1;
    }

    const uint16_t qtype = read_u16(buf + qend - 4);
    const uint16_t qclass = read_u16(buf + qend - 2);

    /* QR=1, AA=1, RD переносимо з запиту як є; RA=1, RCODE=0. */
    buf[OFF_FLAGS_HI] = (uint8_t)(0x84 | (buf[OFF_FLAGS_HI] & 0x01));
    buf[OFF_FLAGS_LO] = 0x80;

    write_u16(buf + OFF_NSCOUNT, 0);
    write_u16(buf + OFF_ARCOUNT, 0);

    const bool answerable = (qtype == DNS_TYPE_A) && (qclass == DNS_CLASS_IN);
    if (!answerable) {
        /*
         * На AAAA та інші типи віддаємо порожню відповідь без помилки.
         * Клієнт із цього робить висновок «запису такого типу немає»
         * і перепитує адресу типом A — тобто приходить туди, де ми
         * його й чекаємо. Помилка ж (NXDOMAIN) навпаки змусила б
         * телефон вважати мережу непрацездатною.
         */
        write_u16(buf + OFF_ANCOUNT, 0);
        return qend;
    }

    if (qend + DNS_ANSWER_LEN > DNS_BUFFER_SIZE) {
        return -1;
    }

    write_u16(buf + OFF_ANCOUNT, 1);

    uint8_t *rr = buf + qend;
    /* Ім'я не повторюємо: вказівник 0xC00C посилається на QNAME у питанні. */
    rr[0] = 0xC0;
    rr[1] = (uint8_t)DNS_HEADER_LEN;
    write_u16(rr + 2, DNS_TYPE_A);
    write_u16(rr + 4, DNS_CLASS_IN);
    rr[6] = 0;
    rr[7] = 0;
    write_u16(rr + 8, DNS_TTL_SECONDS);
    write_u16(rr + 10, 4);
    /* Адреса вже у мережевому порядку байтів — кладемо як є. */
    memcpy(rr + 12, &s_answer_ip, sizeof(s_answer_ip));

    return qend + DNS_ANSWER_LEN;
}

static void dns_server_task(void *arg)
{
    (void)arg;

    uint8_t buffer[DNS_BUFFER_SIZE];

    while (s_running) {
        struct sockaddr_in client_addr;
        socklen_t client_len = sizeof(client_addr);

        const int received = recvfrom(s_sock, buffer, sizeof(buffer), 0,
                                      (struct sockaddr *)&client_addr, &client_len);
        if (received < 0) {
            if (errno == EINTR) {
                continue;
            }
            if (s_running) {
                ESP_LOGE(TAG, "recvfrom: %d (%s)", errno, strerror(errno));
            }
            break;
        }

        const int reply_len = build_response(buffer, received);
        if (reply_len < 0) {
            continue;   /* мовчимо: відповідати на брухт нема сенсу */
        }

        if (sendto(s_sock, buffer, reply_len, 0,
                   (struct sockaddr *)&client_addr, client_len) < 0) {
            ESP_LOGW(TAG, "sendto: %d (%s)", errno, strerror(errno));
        }
    }

    close(s_sock);
    s_sock = -1;
    s_running = false;
    s_task = NULL;

    ESP_LOGI(TAG, "Завдання DNS завершено");
    vTaskDelete(NULL);
}

esp_err_t dns_server_start(uint32_t answer_ip)
{
    if (s_running) {
        return ESP_ERR_INVALID_STATE;
    }

    s_answer_ip = answer_ip;

    s_sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (s_sock < 0) {
        ESP_LOGE(TAG, "Не вдалося створити UDP-сокет: %d", errno);
        return ESP_FAIL;
    }

    struct sockaddr_in server_addr = {0};
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(DNS_PORT);

    if (bind(s_sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        ESP_LOGE(TAG, "Порт 53 зайнято або недоступний: %d", errno);
        close(s_sock);
        s_sock = -1;
        return ESP_FAIL;
    }

    s_running = true;

    /*
     * 3072 байти стеку: 512 з них з'їдає буфер пакета, решта йде на
     * внутрішні структури сокетів LWIP і кадри викликів. Завдання живе
     * окремо від веб-сервера, тож резолюція імен лишається миттєвою
     * навіть тоді, коли той віддає сторінку або сканує ефір.
     */
    if (xTaskCreate(dns_server_task, "dns_server", DNS_TASK_STACK,
                    NULL, DNS_TASK_PRIO, &s_task) != pdPASS) {
        s_running = false;
        close(s_sock);
        s_sock = -1;
        return ESP_ERR_NO_MEM;
    }

    ESP_LOGI(TAG, "Catch-all DNS слухає порт %d", DNS_PORT);
    return ESP_OK;
}

void dns_server_stop(void)
{
    if (!s_running) {
        return;
    }

    s_running = false;

    /*
     * Завдання стоїть у блокувальному recvfrom. shutdown() пробуджує його
     * помилкою, після чого воно саме закриває дескриптор і зникає.
     */
    if (s_sock >= 0) {
        shutdown(s_sock, SHUT_RDWR);
    }

    while (s_task != NULL) {
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
