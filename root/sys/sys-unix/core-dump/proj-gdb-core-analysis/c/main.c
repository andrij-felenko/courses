#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <stdint.h>

typedef struct {
    uint32_t magic;
    uint32_t payload_len;
    char* payload_ptr;
} packet_header_t;

typedef struct {
    packet_header_t* pkt;
    int thread_id;
} thread_arg_t;

void* process_packet(void* arg) {
    thread_arg_t* tinfo = (thread_arg_t*)arg;
    usleep(50000 * tinfo->thread_id);
    
    if (tinfo->thread_id == 2) {
        // Штучна помилка: обнуляємо вказівник у 2-му потоці без м'ютекса
        tinfo->pkt->payload_ptr = NULL;
    }
    
    // Спроба зчитати дані за вказівником викликає SIGSEGV у потоці
    printf("Thread %d byte: %d\n", tinfo->thread_id, tinfo->pkt->payload_ptr[0]);
    return NULL;
}

int main(void) {
    char data_buffer[] = "CRASH_DATA_PAYLOAD";
    packet_header_t pkt = {
        .magic = 0xDEADBEEF,
        .payload_len = sizeof(data_buffer),
        .payload_ptr = data_buffer
    };

    pthread_t threads[4];
    thread_arg_t targs[4];

    for (int i = 0; i < 4; ++i) {
        targs[i].pkt = &pkt;
        targs[i].thread_id = i + 1;
        pthread_create(&threads[i], NULL, process_packet, &targs[i]);
    }

    for (int i = 0; i < 4; ++i) {
        pthread_join(threads[i], NULL);
    }
    return 0;
}
