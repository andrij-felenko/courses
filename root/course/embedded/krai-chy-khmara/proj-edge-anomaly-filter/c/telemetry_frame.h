#ifndef EDGE_TELEMETRY_FRAME_H
#define EDGE_TELEMETRY_FRAME_H

#include <stddef.h>
#include <stdint.h>

#include "edge_detector.h"

/*
 * Бінарний кадр для радіоканалу (LoRa, NB-IoT, BLE). Порядок байтів —
 * молодшим уперед, як у самого мікроконтролера: жодних перетворень.
 *
 *   зсув  розмір  поле
 *   0     1       0x7E                         магічний байт
 *   1     1       версія<<4 | прапорці         версія 1; біт 0 — відмова давача
 *   2     1       дія (telemetry_action_t)
 *   3     4       мітка часу, мс
 *   7     4       значення, float
 *   11    4       середнє, float
 *   15    4       СКВ, float
 *   19    2       z, беззнакове Q8.8 (0xFFFF — насичення)
 *   21    1       довжина знімка, 0..32
 *   22    2*N     знімок: (x - середнє)*100, int16; -32768 — вибірка невалідна
 *   ..    2       CRC-16/CCITT-FALSE по всіх попередніх байтах
 *
 * Знімок їде у фіксованій комі відносно середнього, а не масивом float:
 * 64 байти замість 128. На LoRa SF12 кожні зайві 50 байт — це зайва секунда
 * в ефірі й зайвий мілі-ампер-час з батареї.
 */
#define TELEMETRY_FRAME_MAX_SIZE  (22u + 2u * RING_BUFFER_CAPACITY + 2u)
#define TELEMETRY_SNAPSHOT_INVALID  ((int16_t)-32768)

/* Пакує звіт і знімок у out. Повертає довжину кадру або 0, якщо буфер малий.
   snapshot може бути NULL — тоді кадр іде без передісторії. */
size_t telemetry_frame_encode(const telemetry_report_t *report,
                              const float *snapshot,
                              uint32_t snapshot_len,
                              uint8_t *out,
                              size_t out_cap);

uint16_t telemetry_crc16(const uint8_t *data, size_t len);

#endif /* EDGE_TELEMETRY_FRAME_H */
