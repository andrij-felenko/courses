/**
 * @brief Валідація та обчислення схеми C_n(x, a_n) (C API)
 */
PPolyStatus p_poly_validate_circuit(
    const CircuitHeader *header,
    const void *gates
);

PPolyStatus p_poly_evaluate(
    const CircuitHeader *header,
    const void *gates,
    const uint8_t *input_x,
    const uint8_t *advice_a,
    uint8_t *out_result
);
