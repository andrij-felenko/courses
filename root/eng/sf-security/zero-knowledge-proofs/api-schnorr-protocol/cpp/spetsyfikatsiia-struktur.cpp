#include <cstdint>
#include <cstddef>

// Перелік статусів виконання операцій та кодів помилок
enum class ZkpStatus : uint32_t {
    SUCCESS               = 0x00, // Операція виконана успішно
    ERR_INVALID_PARAMS    = 0x01, // Некоректні математичні параметри групи (p, q, g)
    ERR_OUT_OF_RANGE      = 0x02, // Вхідні дані виходять за дозволені межі полів
    ERR_ZERO_COMMITMENT   = 0x03, // Згенеровано тривіальне зобов'язання r = 0 або r = 1
    ERR_VERIFICATION_FAIL = 0x04, // Математична тотожність g^s ≡ r * y^c не справдилася
    ERR_NONCE_REUSE       = 0x05, // Виявлено повторне використання тимчасового nonce k
    ERR_NULL_POINTER      = 0x06, // Передано нульовий вказівник на буфер даних
    ERR_BUFFER_TOO_SMALL  = 0x07  // Розмір вихідного буфера є недостатнім
};

// Контейнер публічних параметрів групи
struct SchnorrGroupParams {
    const uint8_t* p_bytes;  // Буфер байтів модуля p (big-endian)
    size_t         p_len;    // Довжина p у байтах (наприклад, 256 або 384)
    const uint8_t* q_bytes;  // Буфер байтів порядку q (big-endian)
    size_t         q_len;    // Довжина q у байтах (наприклад, 32)
    const uint8_t* g_bytes;  // Буфер байтів генератора g (big-endian)
    size_t         g_len;    // Довжина g у байтах
};

// Контейнер пакетного неінтерактивного доказу π = (r, s)
struct SchnorrProof {
    uint8_t r_bytes[384];    // Зобов'язання r (розмір відповідає p_len)
    size_t  r_len;
    uint8_t s_bytes[32];     // Відповідь s (розмір відповідає q_len)
    size_t  s_len;
};

// Контейнер стану детермінованого генератора nonce за RFC 6979
struct SchnorrRfc6979State {
    uint8_t v_key[32];       // Внутрішній вектор V для HMAC-SHA256
    uint8_t k_key[32];       // Внутрішній ключ K для HMAC-SHA256
    size_t  hash_len;
};
