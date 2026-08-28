/**
 * @brief Обчислює тристимульні значення XYZ за дискретним спектром випромінювання.
 * 
 * Функція перевіряє цілісність масиву spectrum, завантажує внутрішні таблиці
 * функцій чутливості CIE 1931 та виконує інтегрування методом трапецій.
 * 
 * @param[in]  spectrum Указник на валідну структуру спектральних даних.
 * @param[out] out_xyz  Указник на об'єкт для збереження тристимульних значень.
 * @return COLORIMETRY_OK при успіху або відповідний код помилки.
 */
colorimetry_error_t colorimetry_compute_xyz(
    const spectral_data_t* spectrum,
    tristimulus_xyz_t*      out_xyz
);
