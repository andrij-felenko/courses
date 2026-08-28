/**
 * @brief Розраховує загальний індекс кольоропередачі R_a та спеціальні індекси R1..R15.
 * 
 * @param[in]  spectrum Указник на спектр випробовуваного джерела.
 * @param[in]  cct_info Попередньо обчислені дані CCT та Duv.
 * @param[out] out_cri  Указник на структуру для збереження результатів CRI.
 * @return COLORIMETRY_OK при успіху або відповідний код помилки.
 */
colorimetry_error_t colorimetry_compute_cri(
    const spectral_data_t* spectrum,
    const cct_result_t*    cct_info,
    cri_result_t*          out_cri
);
