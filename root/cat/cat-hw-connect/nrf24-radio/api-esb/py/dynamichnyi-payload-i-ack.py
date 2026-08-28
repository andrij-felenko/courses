FEATURE       = 0x1D
DYNPD         = 0x1C
EN_DPL        = 2
EN_ACK_PAY    = 1
W_ACK_PAYLOAD = 0xA8

# увімкнути динамічний payload + ACK-payload для труби 1
def enable_dynamic_ack_payload():
    write_reg(FEATURE, (1 << EN_DPL) | (1 << EN_ACK_PAY))
    write_reg(DYNPD, (1 << 1))              # динамічна довжина на трубі 1

# приймач: заздалегідь покласти вантаж у ACK для труби 1
def load_ack_payload(data):
    # молодші 3 біти команди — номер труби; далі самі байти вантажу
    spi.xfer2([W_ACK_PAYLOAD | 1] + list(data))
