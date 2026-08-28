# Розпорядник сидить на шині PMBus (двопровідній, як I²C) за адресою 0x40.
SEQ_ADDR        = 0x40
CMD_READ_VOUT   = 0x8B    # стандартна команда PMBus: напруга каналу
CMD_STATUS_WORD = 0x79    # зведений статус: є збій / який саме

def seq_read_vout(bus, channel):
    """Прочитати напругу одного каналу (повертає «сире» 16-розрядне слово)."""
    bus.write_byte_data(SEQ_ADDR, 0x00, channel)   # PAGE: обрати канал
    return bus.read_word_data(SEQ_ADDR, CMD_READ_VOUT)

def seq_first_check(bus):
    st = bus.read_word_data(SEQ_ADDR, CMD_STATUS_WORD)
    if st == 0xFFFF:              # шина «висить» у одиницях — чип не відповів
        log("seq: немає відповіді — перевір живлення й адресу")
        return
    for ch in range(4):
        v = seq_read_vout(bus, ch)
        log(f"seq: канал {ch} = {v} (сире)")   # звірити з очікуваним рівнем
