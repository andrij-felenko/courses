/**
 * @brief Обчислює корельовану колірну температуру (CCT) та відхилення Duv.
 * 
 * Використовує поєднання поліноміальної формули МакКамі для швидкої первинної оцінки
 * та чисельний метод Охно для знаходження точної проекції на лінію чорного тіла.
 * 
 * @param[in]  chroma  Указник на координати хроматичності.
 * @param[out] out_cct Указник на результат CCT.
 * @return COLORIMETRY_OK при успіху або COLORIMETRY_ERR_OUT_OF_RANGE.
 */
colorimetry_error_t colorimetry_compute_cct(
    const chromaticity_coords_t* chroma,
    cct_result_t*                out_cct
);
