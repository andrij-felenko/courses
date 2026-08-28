/* Конфігурація середовища виконання GPU CUDA */
typedef struct {
    int32_t device_id;         /* Ідентифікатор відеокарти (0, 1, ...) */
    void *cuda_stream;         /* Дескриптор потоку cudaStream_t */
    bool enable_p2p_access;    /* Дозволити прямий обмін між кількома GPU */
} msm_cuda_config_t;

/**
 * Ініціалізація GPU-контексту для кривої.
 */
msm_status_t msm_cuda_init_context(msm_cuda_config_t *cuda_cfg, msm_curve_id_t curve);

/**
 * Звільнення виділеної пам'яті на графічному процесорі.
 */
void msm_cuda_release_context(msm_cuda_config_t *cuda_cfg);
