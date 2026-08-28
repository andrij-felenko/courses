/* Бітові маски визначення типу кадру */
#define HDLC_TYPE_MASK          0x01
#define HDLC_TYPE_IS_I(c)       (((c) & HDLC_TYPE_MASK) == 0x00)
#define HDLC_TYPE_IS_S(c)       (((c) & 0x03) == 0x01)
#define HDLC_TYPE_IS_U(c)       (((c) & 0x03) == 0x03)

/* Виділення номерів послідовності для Modulo 8 */
#define HDLC_MOD8_GET_NS(c)     (((c) >> 1) & 0x07)
#define HDLC_MOD8_GET_NR(c)     (((c) >> 5) & 0x07)
#define HDLC_MOD8_GET_PF(c)     (((c) >> 4) & 0x01)

/* Коди команд S-кадрів (біти 2..3) */
#define HDLC_S_CMD_MASK         0x0C
#define HDLC_S_CMD_RR           0x00
#define HDLC_S_CMD_RNR          0x04
#define HDLC_S_CMD_REJ          0x08
#define HDLC_S_CMD_SREJ         0x0C

#define HDLC_S_IS_RR(c)         (((c) & HDLC_S_CMD_MASK) == HDLC_S_CMD_RR)
#define HDLC_S_IS_RNR(c)        (((c) & HDLC_S_CMD_MASK) == HDLC_S_CMD_RNR)
#define HDLC_S_IS_REJ(c)        (((c) & HDLC_S_CMD_MASK) == HDLC_S_CMD_REJ)
#define HDLC_S_IS_SREJ(c)       (((c) & HDLC_S_CMD_MASK) == HDLC_S_CMD_SREJ)
