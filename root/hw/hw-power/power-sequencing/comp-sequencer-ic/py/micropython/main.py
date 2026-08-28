# Розпорядник сидить на шині PMBus (двопровідній, як I²C) за адресою 0x40.
SEQ_ADDR        = 0x40
CMD_READ_VOUT   = 0x8B    # стандартна команда PMBus: напруга каналу
CMD_STATUS_WORD = 0x79    # зведений статус: є збій / який саме

def seq_read_vout(i2c, channel):
    # Прочитати напругу одного каналу (повертає «сире» 16-розрядне слово).
    i2c.writeto_mem(SEQ_ADDR, 0x00, bytes([channel]))   # PAGE: обрати канал
    raw = i2c.readfrom_mem(SEQ_ADDR, CMD_READ_VOUT, 2)
    return raw[0] | (raw[1] << 8)                        # PMBus — молодший байт перший

def seq_first_check(i2c):
    raw = i2c.readfrom_mem(SEQ_ADDR, CMD_STATUS_WORD, 2)
    st = raw[0] | (raw[1] << 8)
    if st == 0xFFFF:              # шина «висить» у одиницях — чип не відповів
        print("seq: немає відповіді — перевір живлення й адресу")
        return
    for ch in range(4):
        v = seq_read_vout(i2c, ch)
        print("seq: канал", ch, "=", v, "(сире)")   # звірити з очікуваним рівнем
