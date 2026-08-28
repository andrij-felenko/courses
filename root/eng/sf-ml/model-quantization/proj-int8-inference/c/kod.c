#include <stdint.h>

typedef struct {
    int32_t  in_dim;       /* довжина вектора входу                        */
    int32_t  out_dim;      /* кількість вихідних нейронів (рядків W)       */
    const int8_t  *W;      /* ваги, out_dim×in_dim, рядок за рядком        */
    const int32_t *bias;   /* зсув, у масштабі акумулятора (int32)         */
    const int32_t *M0;     /* реквант-множник Q31 на КОЖЕН вихід (per-channel) */
    const int32_t *shift;  /* правий зсув n на КОЖЕН вихід (≥ 0)           */
    int32_t  in_zp;        /* zero-point входу  z_x                        */
    int32_t  out_zp;       /* zero-point виходу z_вих                      */
} DenseLayerS8;
