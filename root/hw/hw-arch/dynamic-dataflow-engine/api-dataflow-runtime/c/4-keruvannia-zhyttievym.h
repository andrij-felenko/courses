typedef struct {
    uint32_t worker_threads;       /* Кількість потоків-обчислювачів (0 = автовизначення) */
    size_t   token_queue_capacity; /* Розмір буфера черги токенів (степінь 2) */
    uint32_t max_frames;           /* Розмір пулу кадрів активації */
    uint32_t slots_per_frame;      /* Кількість операндних слотів у кожному кадрі */
} df_engine_cfg_t;

typedef struct df_engine df_engine_t;

df_status_t df_engine_init(
    df_engine_t**          out_engine,
    const df_engine_cfg_t* cfg
);

df_status_t df_engine_shutdown(df_engine_t* engine);
