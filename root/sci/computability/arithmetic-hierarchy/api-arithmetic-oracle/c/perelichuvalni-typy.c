typedef enum {
    AH_CLASS_DELTA_0 = 0,  /* Обчислювані предикати з обмеженими кванторами */
    AH_CLASS_SIGMA_N = 1,  /* Клас Sigma_n^0 (починається з квантора існування EXISTS) */
    AH_CLASS_PI_N    = 2,  /* Клас Pi_n^0 (починається з квантора загальності FORALL) */
    AH_CLASS_DELTA_N = 3   /* Клас Delta_n^0 = Sigma_n^0 ∩ Pi_n^0 (відносно розв'язні) */
} ah_class_type_t;

typedef enum {
    AH_QUANT_EXISTS = 0,   /* Необмежений або обмежений квантор існування (EXISTS) */
    AH_QUANT_FORALL = 1    /* Необмежений або обмежений квантор загальності (FORALL) */
} ah_quantifier_kind_t;
