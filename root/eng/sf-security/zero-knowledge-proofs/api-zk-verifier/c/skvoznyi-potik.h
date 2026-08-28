/**
 * @brief Ініціалізація нової верифікаційної сесії.
 * @param session Вказівник на структуру сесії.
 * @param protocol Ідентифікатор криптографічного протоколу.
 * @param public_inputs Масив публічних даних x.
 * @param inputs_len Кількість елементів публічного входу.
 * @return ZK_SUCCESS або код помилки.
 */
int32_t zk_verifier_init(
    zk_interactive_session_t *session,
    zk_protocol_id_t          protocol,
    const zk_field_element_t *public_inputs,
    uint32_t                  inputs_len
);

/**
 * @brief Прийом зобов'язання R від доводжувача та перехід у стан WAITING_COMMITMENT.
 * @param session Вказівник на активну сесію.
 * @param commitment_R Байт-масив зобов'язання R.
 * @return ZK_SUCCESS у разі коректності елемента.
 */
int32_t zk_verifier_process_commitment(
    zk_interactive_session_t *session,
    const zk_field_element_t *commitment_R
);

/**
 * @brief Генерація криптографічно стійкого виклику e (Challenge).
 * @param session Вказівник на активну сесію.
 * @param out_challenge Буфер для запису згенерованого числа e.
 * @return ZK_SUCCESS при успішній генерації з системного джерела CSPRNG.
 */
int32_t zk_verifier_generate_challenge(
    zk_interactive_session_t *session,
    zk_field_element_t       *out_challenge
);

/**
 * @brief Отримання відповіді s, перевірка алгебраїчного рівняння та фіналізація.
 * @param session Вказівник на активну сесію.
 * @param response_s Байт-масив відповіді s.
 * @return ZK_SUCCESS якщо доказ прийнято, або ZK_ERR_VERIFICATION_FAILED при відхиленні.
 */
int32_t zk_verifier_process_response(
    zk_interactive_session_t *session,
    const zk_field_element_t *response_s
);
