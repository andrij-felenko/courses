typedef enum {
    KALMAR_NODE_CONST       = 0x01,  /* Числова константа uint64_t */
    KALMAR_NODE_VAR         = 0x02,  /* Читання змінної за індексом середовища */
    KALMAR_NODE_ADD         = 0x10,  /* Додавання (lhs + rhs) */
    KALMAR_NODE_SUB         = 0x11,  /* Зрізане віднімання (lhs ∸ rhs) */
    KALMAR_NODE_MUL         = 0x12,  /* Множення (lhs · rhs) */
    KALMAR_NODE_DIV         = 0x13,  /* Безпечне цілочисельне ділення */
    KALMAR_NODE_EXP         = 0x14,  /* Цілочисельне піднесення до степеня */
    KALMAR_NODE_SUM         = 0x20,  /* Обмежена сума ∑_{z ≤ bound} body */
    KALMAR_NODE_PROD        = 0x21,  /* Обмежений добуток ∏_{z ≤ bound} body */
    KALMAR_NODE_SEARCH      = 0x22   /* Обмежений μ-пошук найменшого кореня */
} KalmarNodeType;
