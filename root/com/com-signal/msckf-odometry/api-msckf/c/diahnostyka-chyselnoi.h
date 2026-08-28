/* Коди помилок функцій бібліотеки */
typedef enum {
    MSCKF_SUCCESS = 0,
    MSCKF_ERROR_INVALID_ARGUMENT = -1,
    MSCKF_ERROR_NOT_INITIALIZED = -2,
    MSCKF_ERROR_TIME_REGRESSION = -3,
    MSCKF_ERROR_NUMERICAL_DIVERGENCE = -4
} MsckfStatus;

/* Непрозора структура рушія */
typedef struct MsckfContext MsckfContext;

/* 1. Створення та ініціалізація екземпляра */
MsckfContext* msckf_create(const MsckfConfig* config);
void msckf_destroy(MsckfContext* ctx);
MsckfStatus msckf_reset(MsckfContext* ctx);

/* 2. Подання вимірів */
MsckfStatus msckf_feed_imu(MsckfContext* ctx, const MsckfImuMeasurement* imu);
MsckfStatus msckf_feed_frame(MsckfContext* ctx, const MsckfFeatureFrame* frame);

/* 3. Зчитування результатів */
MsckfStatus msckf_get_estimate(const MsckfContext* ctx, MsckfEstimate* out_est);
MsckfStatus msckf_get_diagnostics(const MsckfContext* ctx, MsckfDiagnostics* out_diag);
