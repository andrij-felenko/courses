typedef enum {
    AT_RES_OK = 0,
    AT_RES_ERROR,
    AT_RES_TIMEOUT,
    AT_RES_BUSY
} at_result_t;

typedef void (*at_cmd_cb_t)(at_result_t result, const char *resp_data, void *user_ctx);

typedef struct {
    const char    *cmd_str;         /* Текст команди, наприклад "AT+CSQ\r\n" */
    const char    *expect_prefix;   /* Очікуваний префікс даних, наприклад "+CSQ:" */
    uint32_t       timeout_ms;      /* Індивідуальний таймаут виконання */
    uint8_t        max_retries;     /* Ліміт повторних спроб при збої */
    uint8_t        current_retry;   /* Поточна спроба */
    at_cmd_cb_t    callback;        /* Функція зворотної реакції */
    void          *user_ctx;        /* Контекст користувача */
} at_cmd_desc_t;
