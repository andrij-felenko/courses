/**
 * Емуляція виклику EVM Precompile G1 MSM.
 * @param out_data   Буфер returndata (64 байти для BN254 або 96 байтів для BLS12-381).
 * @param in_data    Буфер calldata (послідовність пар точка || скаляр).
 * @param in_len     Розмір calldata у байтах.
 * @param curve      Ідентифікатор кривої.
 * @return 0 у разі успіху, ненульовий код помилки EVM revert.
 */
int32_t msm_evm_precompile_call(
    uint8_t *out_data,
    const uint8_t *in_data,
    size_t in_len,
    msm_curve_id_t curve
);
