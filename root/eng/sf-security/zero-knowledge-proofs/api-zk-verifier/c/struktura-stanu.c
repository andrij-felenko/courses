typedef enum {
    ZK_STATE_UNINITIALIZED = 0,
    ZK_STATE_WAITING_COMMITMENT = 1,
    ZK_STATE_CHALLENGE_GENERATED = 2,
    ZK_STATE_VERIFIED_ACCEPTED = 3,
    ZK_STATE_VERIFIED_REJECTED = 4,
    ZK_STATE_ERROR = 5
} zk_verifier_state_t;

typedef struct {
    zk_protocol_id_t     protocol_id;     /* Ідентифікатор типу протоколу */
    zk_verifier_state_t  state;           /* Поточний стан автомата */
    uint64_t             session_id;      /* Унікальний ID сесії взаємодії */
    uint32_t             security_bits;   /* Рівень безпеки (наприклад, 128 або 256 біт) */
    
    zk_field_element_t   public_input[8];  /* Загальнодоступний вхід x */
    uint32_t             public_input_len;
    
    zk_field_element_t   commitment_R;    /* Зобов'язання R від доводжувача */
    zk_field_element_t   challenge_e;     /* Випадковий виклик верифікатора */
    zk_field_element_t   response_s;      /* Відповідь s від доводжувача */
} zk_interactive_session_t;
