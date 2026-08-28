/* ldpc_codec.h — C API для бібліотеки libldpc */
#ifndef LDPC_CODEC_H
#define LDPC_CODEC_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Непрозорий тип контексту кодека */
typedef struct ldpc_codec_s ldpc_codec_t;

/**
 * @brief Створює екземпляр LDPC-кодека та ініціалізує внутрішні графи Таннера.
 * @param config Вказівник на структуру конфігурації.
 * @param[out] codec_out Вказівник для повернення створеного контексту.
 * @return LDPC_SUCCESS у разі успіху, або код помилки.
 */
ldpc_status_t ldpc_codec_create(const ldpc_config_t *config, ldpc_codec_t **codec_out);

/**
 * @brief Звільняє всі ресурси, виділені для екземпляра кодека.
 * @param codec Контекст кодека.
 */
void ldpc_codec_destroy(ldpc_codec_t *codec);

/**
 * @brief Виконує систематичне кодування інформаційного вектора u у кодове слово c.
 * @param codec Контекст кодека.
 * @param info_bits Вхідний масив інформаційних бітів довжиною (n - m).
 * @param info_len Довжина вхідного масиву бітів.
 * @param[out] codeword_out Вихідний буфер для кодового слова довжиною n бітів.
 * @param codeword_len Розмір вихідного бувера.
 * @return LDPC_SUCCESS у разі успіху.
 */
ldpc_status_t ldpc_encode(const ldpc_codec_t *codec, 
                          const uint8_t *info_bits, size_t info_len,
                          uint8_t *codeword_out, size_t codeword_len);

/**
 * @brief Виконує ітеративне декодування вектора LLR каналу.
 * @param codec Контекст кодека.
 * @param channel_llr Вхідний масив дробових LLR довжиною n.
 * @param llr_len Довжина масиву LLR.
 * @param[out] decoded_bits_out Вихідний буфер для виправлених бітів (n бітів).
 * @param bits_len Розмір вихідного буфера.
 * @param[out] iters_performed Необов'язковий вказівник для повернення кількості виконаних ітерацій.
 * @return LDPC_SUCCESS у разі збіжності синдрому, або LDPC_ERROR_MAX_ITERATIONS.
 */
ldpc_status_t ldpc_decode(ldpc_codec_t *codec,
                          const float *channel_llr, size_t llr_len,
                          uint8_t *decoded_bits_out, size_t bits_len,
                          uint32_t *iters_performed);

/**
 * @brief Динамічно змінює параметри декодування без перестворення графа.
 * @param codec Контекст кодека.
 * @param algo Новий алгоритм декодування.
 * @param max_iterations Новий ліміт ітерацій.
 * @return LDPC_SUCCESS або код помилки.
 */
ldpc_status_t ldpc_codec_set_params(ldpc_codec_t *codec, ldpc_algo_t algo, uint32_t max_iterations);

/**
 * @brief Повертає текстовий опис коду помилки.
 * @param status Код статусу.
 * @return Рядок C із текстовим описом.
 */
const char* ldpc_status_to_string(ldpc_status_t status);

#ifdef __cplusplus
}
#endif

#endif /* LDPC_CODEC_H */
