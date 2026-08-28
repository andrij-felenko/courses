typedef struct {
    zk_curve_point_g1_t  pi_a;            /* Елемент A у групі G1 */
    zk_curve_point_g2_t  pi_b;            /* Елемент B у групі G2 */
    zk_curve_point_g1_t  pi_c;            /* Елемент C у групі G1 */
} zk_snark_groth16_proof_t;

typedef struct {
    zk_curve_point_g1_t  alpha_g1;
    zk_curve_point_g2_t  beta_g2;
    zk_curve_point_g2_t  gamma_g2;
    zk_curve_point_g2_t  delta_g2;
    zk_curve_point_g1_t *ic_query;       /* Масив точок публічного входу */
    uint32_t             ic_query_len;
} zk_verification_key_t;
