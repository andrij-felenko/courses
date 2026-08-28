/**
 * @brief Обчислює цикл Міллера f_{T, Q}(P) без фінального піднесення до степеня.
 * @param[out] out_gt Елемент поля F_{p^{12}} для запису накопиченого результату.
 * @param[in] P Точка групи G1 (в афінних координатах).
 * @param[in] Q Точка групи G2 (в афінних координатах).
 */
bls12_381_status_t bls12_381_pairing_miller_loop(
    bls12_381_gt_t* out_gt,
    const bls12_381_g1_affine_t* P,
    const bls12_381_g2_affine_t* Q
);

/**
 * @brief Пакетне (мульти-) спарювання: ∏_{i=0}^{N-1} e(P_i, Q_i).
 * @param[out] out_gt Результальний елемент Gt.
 * @param[in] P_array Масив з N точок групи G1.
 * @param[in] Q_array Масив з N точок групи G2.
 * @param[in] count Кількість пар N.
 */
bls12_381_status_t bls12_381_multi_pairing(
    bls12_381_gt_t* out_gt,
    const bls12_381_g1_affine_t* P_array,
    const bls12_381_g2_affine_t* Q_array,
    size_t count
);
