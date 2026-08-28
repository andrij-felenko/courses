// packet_worker.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>

typedef struct {
    char header[8];
    void (*handler)(const char *);
} PacketContext;

void default_logger(const char *msg) {
    printf("[LOG] %s\n", msg);
}

void parse_payload(const char *input, size_t len) {
    char local_buffer[16];
    // Прихована помилка: відсутність перевірки меж len
    // Якщо len > 16, запис затирає сусідні структури на стеку
    memcpy(local_buffer, input, len);
    local_buffer[15] = '\0';
}

void process_network_event(int event_id) {
    PacketContext ctx;
    memcpy(ctx.header, "PKT_HDR", 8);
    ctx.handler = default_logger;

    // Псевдовипадковий генератор розміру для моделювання плаваючого збою
    size_t payload_len = 12 + (rand() % 16); // Довжина від 12 до 27 байтів

    char payload_data[32];
    memset(payload_data, 'A', sizeof(payload_data));

    // Якщо payload_len > 24, пошкоджується покажчик ctx.handler
    parse_payload(payload_data, payload_len);

    if (event_id % 1000 == 0) {
        ctx.handler("Packet processed successfully.");
    }
}

int main(int argc, char **argv) {
    srand(time(NULL));
    printf("[START] Processing network stream...\n");

    for (int i = 0; i < 50000; ++i) {
        process_network_event(i);
    }

    printf("[FINISH] All packets processed without crash.\n");
    return 0;
}
