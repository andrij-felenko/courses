// Маска прапорця наявності підпису у полі incompat_flags (байт 2 кадру)
#define MAVLINK_IFLAG_SIGNED                 0x01

// Фіксована довжина блоку підпису у фізичному кадрі (байти)
#define MAVLINK_SIGNATURE_BLOCK_LEN          13

// Прапорці конфігурації у структурі mavlink_signing_t
#define MAVLINK_SIGNING_FLAG_SIGN_OUTGOING   0x01

// Коди статусу кадрування у структурі mavlink_status_t
#define MAVLINK_FRAMING_INCOMPLETE           0
#define MAVLINK_FRAMING_OK                   1
#define MAVLINK_FRAMING_BAD_CRC              2
#define MAVLINK_FRAMING_BAD_SIGNATURE        3

// Максимальна кількість незалежних потоків підпису в таблиці сесій
#define MAVLINK_MAX_SIGNING_STREAMS          16
