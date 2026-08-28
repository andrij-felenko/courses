#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <duckdb.h>

void execute_vectorized_analytics(void) {
    duckdb_database db;
    duckdb_connection con;

    /* Створення in-memory бази даних у адресному просторі процесу */
    if (duckdb_open(NULL, &db) == DuckDBError) {
        fprintf(stderr, "Помилка ініціалізації in-memory бази DuckDB\n");
        return;
    }

    if (duckdb_connect(db, &con) == DuckDBError) {
        duckdb_close(&db);
        return;
    }

    /* Створення таблиці та генерація 100 000 рядків тестових даних */
    duckdb_query(con, "CREATE TABLE telemetry (id BIGINT, sensor_val DOUBLE, status INTEGER);", NULL);
    duckdb_query(con, "INSERT INTO telemetry SELECT range, random() * 100.0, (range % 5)::INT FROM range(100000);", NULL);

    /* Виконання фільтрації та вибірки */
    duckdb_result result;
    if (duckdb_query(con, "SELECT id, sensor_val FROM telemetry WHERE status = 0;", &result) == DuckDBError) {
        fprintf(stderr, "Помилка запиту: %s\n", duckdb_result_error(&result));
        duckdb_destroy_result(&result);
        duckdb_disconnect(&con);
        duckdb_close(&db);
        return;
    }

    /* Отримання результатів через векторизовані пакети DataChunk */
    idx_t chunk_count = duckdb_result_chunk_count(result);
    for (idx_t i = 0; i < chunk_count; ++i) {
        duckdb_data_chunk chunk = duckdb_result_get_chunk(result, i);
        idx_t row_count = duckdb_data_chunk_get_size(chunk);

        /* Отримання векторів відповідних стовпців */
        duckdb_vector id_vec = duckdb_data_chunk_get_vector(chunk, 0);
        duckdb_vector val_vec = duckdb_data_chunk_get_vector(chunk, 1);

        /* Прямі покажчики на неперервні масиви пам'яті */
        int64_t *id_data = (int64_t*)duckdb_vector_get_data(id_vec);
        double *val_data = (double*)duckdb_vector_get_data(val_vec);

        /* Пакетне опрацювання векторів без копіювання */
        for (idx_t r = 0; r < row_count; ++r) {
            int64_t record_id = id_data[r];
            double value = val_data[r];
            (void)record_id;
            (void)value;
        }

        duckdb_destroy_data_chunk(&chunk);
    }

    duckdb_destroy_result(&result);
    duckdb_disconnect(&con);
    duckdb_close(&db);
}
