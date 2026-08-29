// Валідація вхідного кадру на приймачі (C99).
#include "receiver.h"

#include <string.h>

void device_link_init(device_link_t *link)
{
    if (link != NULL) {
        memset(link, 0, sizeof(*link));
    }
}

frame_status_t device_link_accept(device_link_t *link,
                                  const uint8_t *buf,
                                  size_t len,
                                  telemetry_sample_t *out_sample,
                                  uint16_t *out_seq)
{
    if (link == NULL || buf == NULL || out_sample == NULL) {
        return FRAME_ERR_SHORT;
    }

    // 1. Довжина. Датаграма може бути й довшою (доповнення канального рівня),
    // але коротша за кадр — це вже не кадр, і читати з неї нема чого.
    if (len < sizeof(custom_frame_t)) {
        link->rejected_short++;
        return FRAME_ERR_SHORT;
    }

    // 2. Синхробайт. Найдешевша перевірка йде першою: в ефірі, де слухає
    // будь-хто, більшість сміття відсіюється саме тут, за одне порівняння.
    if (buf[0] != FRAME_MAGIC) {
        link->rejected_magic++;
        return FRAME_ERR_MAGIC;
    }

    // Копіюємо в локальну структуру, а не розіменовуємо буфер приведенням
    // типу. Приймальний буфер драйвера рідко вирівняний на 4 байти, і на
    // Cortex-M0 звертання до 32-бітного поля за непарною адресою — це
    // миттєвий HardFault, а не «трохи повільніше».
    custom_frame_t frame;
    memcpy(&frame, buf, sizeof(frame));

    if (frame.msg_type != FRAME_TYPE_TELEM) {
        link->rejected_type++;
        return FRAME_ERR_TYPE;
    }

    // 3. CRC по тих самих 14 байтах, які рахував відправник.
    uint16_t expected = crc16_ccitt(buf, CUSTOM_FRAME_CRC_LEN);
    if (frame.crc16 != expected) {
        link->rejected_crc++;
        return FRAME_ERR_CRC;
    }

    // 4. Номер послідовності. Наївне порівняння seq <= last_seq ламається на
    // переповненні шістнадцяти бітів: після 65535 лічильник іде на 0, і
    // сервер відкинув би всі наступні кадри як «старі». Тому дивимось на
    // РІЗНИЦЮ у знаковій арифметиці: додатна різниця в межах піввікна
    // (32767 кадрів) означає новий кадр, недодатна — дублікат або повтор.
    if (link->have_seq) {
        int16_t delta = (int16_t)(uint16_t)(frame.seq_num - link->last_seq);
        if (delta <= 0) {
            link->rejected_replay++;
            return FRAME_ERR_REPLAY;
        }
    }

    link->last_seq = frame.seq_num;
    link->have_seq = true;
    link->accepted++;

    out_sample->timestamp_s  = frame.timestamp_s;
    out_sample->temp_centi_c = frame.temp_c;
    out_sample->humidity_pct = frame.hum_pct;
    out_sample->vbat_mv      = frame.vbat_mv;
    if (out_seq != NULL) {
        *out_seq = frame.seq_num;
    }
    return FRAME_OK;
}

const char *frame_status_name(frame_status_t status)
{
    switch (status) {
        case FRAME_OK:            return "OK";
        case FRAME_ERR_SHORT:     return "закоротка датаграма";
        case FRAME_ERR_MAGIC:     return "чужий синхробайт";
        case FRAME_ERR_TYPE:      return "невідомий тип";
        case FRAME_ERR_CRC:       return "CRC не збігається";
        case FRAME_ERR_REPLAY:    return "дублікат або повтор";
        default:                  return "?";
    }
}
