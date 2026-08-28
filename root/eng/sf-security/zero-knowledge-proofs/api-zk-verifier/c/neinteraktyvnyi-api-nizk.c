/**
 * @brief Однокрокова перевірка стислого неінтерактивного доказу ZK-SNARK (Groth16).
 * @param vk Вказівник на перевірочний ключ (Verification Key).
 * @param proof Вказівник на структуру доказу (pi_a, pi_b, pi_c).
 * @param public_inputs Вектор публічних вхідних сигналів.
 * @param inputs_len Кількість публічних сигналів.
 * @return ZK_SUCCESS якщо спарювання e(A,B) == e(alpha,beta) * e(x, gamma) * e(C, delta).
 */
int32_t zk_nizk_groth16_verify(
    const zk_verification_key_t   *vk,
    const zk_snark_groth16_proof_t *proof,
    const zk_field_element_t      *public_inputs,
    uint32_t                       inputs_len
);
