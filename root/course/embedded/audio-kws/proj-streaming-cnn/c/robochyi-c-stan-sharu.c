#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>     // lroundf

// Один causal-згортковий шар над часовою віссю (ядро Kt по часу, 1×1 по частоті
// для стислості прикладу; ширший простір узагальнюється тривіально).
#define KT_MAX   3        // максимальна ширина ядра по часу серед шарів
#define CIN_MAX  64       // максимум вхідних каналів
#define COUT_MAX 64       // максимум вихідних каналів

typedef struct {
    int kt;                                   // ширина ядра по часу (напр. 3)
    int cin, cout;                            // канали входу / виходу
    // ВХІДНЕ КІЛЬЦЕ: kt колонок по cin значень int8, кешованих між кроками.
    int8_t  ring[KT_MAX][CIN_MAX];
    int     w_head;                           // куди ляже НАСТУПНА колонка (= найстаріша зараз)
    int     filled;                           // скільки колонок уже накопичено (для старту)
    // ВАГИ: [cout][kt][cin] int8; зсуви int32 (як у квантованому TFLite).
    const int8_t  *w;                         // розмір cout*kt*cin
    const int32_t *bias;                      // розмір cout
    // Квантування виходу: множник-зсув (спрощений requant одним float для ясності).
    float   out_scale;                        // ціна поділки виходу
    int     out_zp;                           // нульова точка виходу
    int     in_zp;                            // нульова точка входу (від навчання)
} ConvLayer;
