enum class ArithmeticClassType {
    Delta0 = 0,  // Обчислювані предикати з обмеженими кванторами
    SigmaN = 1,  // Клас Sigma_n^0 (починається з квантора існування EXISTS)
    PiN    = 2,  // Клас Pi_n^0 (починається з квантора загальності FORALL)
    DeltaN = 3   // Клас Delta_n^0 = Sigma_n^0 ∩ Pi_n^0 (відносно розв'язні)
};

enum class QuantifierKind {
    Exists = 0,  // Необмежений або обмежений квантор існування (EXISTS)
    Forall = 1   // Необмежений або обмежений квантор загальності (FORALL)
};
