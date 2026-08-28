#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>

/* Сітка слотів. Слот s ↔ клітина (x, y): x = s % W, y = s / W. */
typedef struct {
    int W, H;        /* розміри тканини в слотах */
    int nslots;      /* W · H                    */
} Grid;

/* Список з'єднань у двох дзеркальних таблицях.
   Уперед: виводи сполуки n — net_pins[net_off[n] .. net_off[n+1])
   Назад:  сполуки блока b — blk_nets[blk_off[b] .. blk_off[b+1])
   Друга таблиця й є тим, заради чого все затіяно: вона миттю каже,
   ЯКІ сполуки зачепить ворушіння цього блока. */
typedef struct {
    int nblocks, nnets;
    int *net_off;    /* [nnets + 1]        */
    int *net_pins;   /* [net_off[nnets]]   — номери блоків */
    int *blk_off;    /* [nblocks + 1]      */
    int *blk_nets;   /* [blk_off[nblocks]] — номери сполук  */
} Netlist;

/* Розміщення — теж у два боки, і обидва потрібні щохода. */
typedef struct {
    int *blk_at;     /* [nslots]  який блок сидить у слоті, −1 = порожньо */
    int *slot_of;    /* [nblocks] у якому слоті сидить блок              */
} Placement;

/* Робочі буфери для дельти. */
typedef struct {
    int *mark;       /* [nnets] мітка «сполуку вже взято» = номер ходу */
    int *touched;    /* [nnets] список зачеплених сполук цього ходу    */
    int ntouched;
    int stamp;       /* лічильник ходів — він і є міткою */
} Delta;
