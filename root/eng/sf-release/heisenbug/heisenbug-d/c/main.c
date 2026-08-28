#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

typedef struct {
    int id;
    int payload[64];
} Record;

static Record *g_shared_record = NULL;
static int g_probe_mode = 0;

void *reader_thread(void *arg) {
    long iterations = (long)arg;
    long valid_reads = 0;

    for (long i = 0; i < iterations; ++i) {
        if (g_probe_mode) {
            // Спостережницький ефект: виклик I/O серіалізує потік
            printf("[Reader] Iteration: %ld\n", i);
        }

        Record *rec = g_shared_record;
        if (rec != NULL) {
            // Небезпечне читання без м'ютекса: пам'ять може бути звільнена паралельно
            int first_val = rec->payload[0];
            if (first_val >= 0) {
                valid_reads++;
            }
        }
    }
    return (void *)valid_reads;
}

void *writer_thread(void *arg) {
    long iterations = (long)arg;

    for (long i = 0; i < iterations; ++i) {
        if (g_probe_mode) {
            printf("[Writer] Resetting record %ld\n", i);
        }

        Record *fresh = (Record *)malloc(sizeof(Record));
        fresh->id = (int)i;
        fresh->payload[0] = (int)(i + 1);

        Record *old = g_shared_record;
        g_shared_record = fresh;

        if (old != NULL) {
            // Звільнення попереднього блоку
            free(old);
        }
    }
    return NULL;
}

int main(int argc, char **argv) {
    g_probe_mode = (argc > 1 && argv[1][0] == '1') ? 1 : 0;

    g_shared_record = (Record *)malloc(sizeof(Record));
    g_shared_record->id = 0;
    g_shared_record->payload[0] = 1;

    pthread_t t_read, t_write;
    long iters = 200000;

    pthread_create(&t_read, NULL, reader_thread, (void *)iters);
    pthread_create(&t_write, NULL, writer_thread, (void *)iters);

    pthread_join(t_read, NULL);
    pthread_join(t_write, NULL);

    if (g_shared_record) free(g_shared_record);
    printf("Execution finished successfully.\n");
    return 0;
}
