#ifndef DELAYLINE_H
#define DELAYLINE_H

#include <stdbool.h>
#include <stdint.h>

/* Пакет каналу: одним кадром їде кілька величин — телеметрія несе кут і
   кутову швидкість, командний лінк — положення стіка. */
enum { LINK_PAYLOAD = 2 };
enum { LINK_ANGLE = 0, LINK_RATE = 1, LINK_STICK = 0 };

typedef struct {
    float v[LINK_PAYLOAD];
} LinkPacket;

/* Черга чистої транспортної затримки: дискретний exp(-s*tau).
   Амплітуду не чіпає взагалі — лише зсуває пакет у часі. */
typedef struct {
    LinkPacket *slot;    /* кільце пакетів */
    float      *avail;   /* момент, коли приймач має право взяти пакет */
    int   cap;
    int   head;          /* куди пишемо наступний */
    int   tail;          /* найстаріший ще не виданий */
    int   count;
    float base_delay;    /* стала складова лагу, с */
    float jitter;        /* половина розкиду затримки, с */
    bool  buffered;      /* буфер джитера: сталий лаг найгіршого випадку */
    uint32_t rng;
    LinkPacket last_out; /* останній виданий пакет — застигла картинка */
    int   freezes;       /* кроків, на яких нового пакета не було */
    int   drops;         /* переповнення кільця */
} DelayLine;

bool  delay_init(DelayLine *dl, float base_delay, float jitter, bool buffered,
                 float dt, uint32_t seed);
void  delay_free(DelayLine *dl);
void  delay_push(DelayLine *dl, LinkPacket pkt, float now);
LinkPacket delay_pop(DelayLine *dl, float now);

/* Лаг, який після всіх буферів реально бачить приймач. */
float delay_effective(const DelayLine *dl);
int   delay_freezes(const DelayLine *dl);
int   delay_drops(const DelayLine *dl);

#endif /* DELAYLINE_H */
