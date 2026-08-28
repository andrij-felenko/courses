// Ініціалізація FAPI з використанням системного профілю
TSS2_RC Fapi_Initialize(
    FAPI_CONTEXT **fapiContext, 
    const char *uri
);

// Створення та запечатування секрету за 1 виклик
TSS2_RC Fapi_Seal(
    FAPI_CONTEXT *fapiContext,
    const char *path,                // Шлях до об'єкта "/HS/SRK/my_secret"
    const char *type,                // Тип політики "pcr"
    const uint8_t *data, size_t numData,
    const char *policyPath
);

// Вилучення запечатаного секрету
TSS2_RC Fapi_Unseal(
    FAPI_CONTEXT *fapiContext,
    const char *path,
    uint8_t **data, size_t *numData
);
