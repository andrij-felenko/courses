// Приймальний бік власного протоколу: шлюз або серверний демон (C99).
#ifndef RECEIVER_H
#define RECEIVER_H

#include "telemetry.h"

typedef enum {
    FRAME_OK = 0,
    FRAME_ERR_SHORT,    // датаграма коротша за кадр
    FRAME_ERR_MAGIC,    // не наш кадр: шум, чужий протокол, зсув потоку
    FRAME_ERR_TYPE,     // наш магічний байт, але незнайомий тип повідомлення
    FRAME_ERR_CRC,      // кадр побився в дорозі
    FRAME_ERR_REPLAY    // дублікат або повтор старого кадру
} frame_status_t;

// Стан звʼязку з ОДНИМ пристроєм. Лічильник послідовності має сенс лише в
// парі з відправником, тож на сервері така структура заводиться на кожен
// ідентифікатор вузла.
typedef struct {
    uint16_t last_seq;
    bool     have_seq;          // чи бачили ми від цього вузла бодай один кадр
    uint32_t accepted;
    uint32_t rejected_short;
    uint32_t rejected_magic;
    uint32_t rejected_type;
    uint32_t rejected_crc;
    uint32_t rejected_replay;
} device_link_t;

void device_link_init(device_link_t *link);

// Перевіряє кадр за чотирма ознаками (довжина, магічний байт, CRC, номер
// послідовності) і на успіх кладе виміри в out_sample, а номер — в out_seq.
// out_seq можна передати як NULL, якщо номер не потрібен.
frame_status_t device_link_accept(device_link_t *link,
                                  const uint8_t *buf,
                                  size_t len,
                                  telemetry_sample_t *out_sample,
                                  uint16_t *out_seq);

const char *frame_status_name(frame_status_t status);

#endif // RECEIVER_H
