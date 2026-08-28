/**
 * @brief Розраховує 2D-координати хроматичності x, y (CIE 1931) та u', v' (CIE 1976 UCS).
 * 
 * @param[in]  xyz        Указник на вихідний вектор XYZ.
 * @param[out] out_chroma Указник на об'єкт для збереження координат.
 * @return COLORIMETRY_OK при успіху або COLORIMETRY_ERR_ZERO_INTEGRAL, якщо X+Y+Z == 0.
 */
colorimetry_error_t colorimetry_compute_chromaticity(
    const tristimulus_xyz_t* xyz,
    chromaticity_coords_t*   out_chroma
);
