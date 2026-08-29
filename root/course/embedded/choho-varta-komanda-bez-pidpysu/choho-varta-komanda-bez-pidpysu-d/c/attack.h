#ifndef ATTACK_H
#define ATTACK_H

#include <stdint.h>

#include "oracle.h"

/*
 * Підбір тегу байт за байтом за часом відповіді приймача.
 *
 * Нападник не знає ні ключа, ні алгоритму MAC. Він знає лише те, що приймач
 * відповідає ТРОХИ довше, коли черговий байт тегу вгаданий: порівняння
 * дійшло на один байт далі. Цього досить, щоб замінити перебір 2^256
 * на 32 незалежні перебори по 256 варіантів.
 */

typedef struct {
    uint8_t  tag[TAG_LEN]; /* зібраний нападником тег */
    int      accepted;     /* приймач ПРИЙНЯВ цей тег */
    uint64_t queries;      /* скільки кадрів на це пішло */
} attack_report;

attack_report attack_recover_tag(oracle *o);

#endif /* ATTACK_H */
