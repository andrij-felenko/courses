/* pc.h — включають обидві програми, розкладка мусить збігатися байт у байт */
#ifndef PC_H
#define PC_H

#include <semaphore.h>
#include <stdatomic.h>

#define SHM_NAME "/pc.ring"
#define SLOTS    8u
#define MSGLEN   64u
#define READY    0x50432D31u        /* «PC-1»: область повністю налаштована */

struct ring {
    _Atomic unsigned ready;         /* ставиться ОСТАННІМ і читається ПЕРШИМ */
    sem_t    free_slots;            /* скільки місць вільно */
    sem_t    filled;                /* скільки записів готово */
    sem_t    mutex;                 /* хто зараз чіпає індекси */
    unsigned head, tail;
    char     slot[SLOTS][MSGLEN];
};

#endif
