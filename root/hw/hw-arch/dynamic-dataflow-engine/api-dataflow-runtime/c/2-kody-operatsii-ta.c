typedef enum {
    DF_OP_NOP      = 0x00,  /* Пересилка операнда без змін */
    DF_OP_ADD      = 0x01,  /* Додавання: result = in0 + in1 */
    DF_OP_SUB      = 0x02,  /* Віднімання: result = in0 - in1 */
    DF_OP_MUL      = 0x03,  /* Множення: result = in0 * in1 */
    DF_OP_DIV      = 0x04,  /* Ділення: result = in0 / in1 */
    DF_OP_BRANCH   = 0x05,  /* Умовне розгалуження за предикатом */
    DF_OP_MERGE    = 0x06,  /* Детерміноване злиття потоків */
    DF_OP_I_READ   = 0x07,  /* Нестроге читання з I-структури */
    DF_OP_I_WRITE  = 0x08,  /* Одноразовий запис у I-структуру */
    DF_OP_CALL     = 0x09,  /* Виділення кадру та виклик підграфа */
    DF_OP_RET      = 0x0A   /* Повернення результату у батьківський контекст */
} df_opcode_t;

#define DF_MAX_ARCS 4

typedef struct {
    df_node_id_t dest_node;
    df_port_t    dest_port;
} df_arc_t;

typedef struct {
    df_opcode_t opcode;
    uint8_t     is_binary;     /* 1 = бінарна (потребує ETS), 0 = унарна */
    uint8_t     slot_offset;   /* Зміщення слота в кадрі активації FP + offset */
    uint8_t     arc_count;     /* Кількість вихідних з'єднань (0..DF_MAX_ARCS) */
    df_arc_t    arcs[DF_MAX_ARCS];
} df_node_desc_t;
