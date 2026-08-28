#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <rocksdb/c.h>

void execute_rocksdb_batch(void) {
    rocksdb_options_t *options = rocksdb_options_create();
    rocksdb_options_set_create_if_missing(options, 1);
    rocksdb_options_increase_parallelism(options, 4);

    char *err = NULL;
    rocksdb_t *db = rocksdb_open(options, "embedded_kv.db", &err);
    if (err) {
        fprintf(stderr, "Помилка RocksDB: %s\n", err);
        rocksdb_free(err);
        rocksdb_options_destroy(options);
        return;
    }

    rocksdb_writebatch_t *batch = rocksdb_writebatch_create();
    for (int i = 0; i < 1000; ++i) {
        char key[32], val[64];
        snprintf(key, sizeof(key), "device:%04d:metric", i);
        snprintf(val, sizeof(val), "voltage=220.%d;temp=36.%d", i % 10, i % 10);
        rocksdb_writebatch_put(batch, key, strlen(key), val, strlen(val));
    }

    rocksdb_writeoptions_t *write_opts = rocksdb_writeoptions_create();
    rocksdb_writeoptions_set_sync(write_opts, 0); /* Асинхронний запис у буфер WAL */

    rocksdb_write(db, write_opts, batch, &err);
    if (err) {
        fprintf(stderr, "Помилка пакетного запису: %s\n", err);
        rocksdb_free(err);
    }

    rocksdb_writebatch_destroy(batch);
    rocksdb_writeoptions_destroy(write_opts);
    rocksdb_close(db);
    rocksdb_options_destroy(options);
}
