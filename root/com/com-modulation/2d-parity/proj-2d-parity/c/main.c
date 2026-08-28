#include <stdint.h>
#include <assert.h>

/* Слово коду — rows+1 машинних слів по cols+1 значущих бітів:
     w[r], r < rows  — рядок даних: біти 0..cols-1 дані, біт cols — парність рядка;
     w[rows]         — стрічка парності стовпців, і її біт cols — кут.
   Обмеження: 1 <= cols <= 63 (треба місце під біт парності), 1 <= rows <= 63. */

typedef enum { W2D_CLEAN, W2D_FIXED, W2D_DETECTED } w2d_verdict;

static inline int parity64(uint64_t x)      /* XOR усіх 64 бітів — 6 зсувів */
{
    x ^= x >> 32;
    x ^= x >> 16;
    x ^= x >> 8;
    x ^= x >> 4;
    x ^= x >> 2;
    x ^= x >> 1;
    return (int)(x & 1u);
}

static inline int single_bit(uint64_t x)    /* рівно один встановлений біт? */
{
    return x != 0 && (x & (x - 1)) == 0;
}

static inline int ctz64(uint64_t x)         /* індекс єдиного встановленого біта */
{
    int n = 0;
    while (!(x & 1u)) { x >>= 1; n++; }
    return n;
}

void w2d_encode(uint64_t *w, int rows, int cols)
{
    uint64_t mask, cp = 0;
    int r;

    assert(cols >= 1 && cols <= 63 && rows >= 1 && rows <= 63);
    mask = ((uint64_t)1 << cols) - 1;

    for (r = 0; r < rows; r++) {
        uint64_t d = w[r] & mask;                       /* тільки дані: решту з буфера геть */
        w[r] = d | ((uint64_t)parity64(d) << cols);     /* парність рядка — у біт cols */
        cp ^= w[r];                                     /* усі стовпці разом, і кут теж */
    }
    w[rows] = cp;
}

w2d_verdict w2d_decode(uint64_t *w, int rows, int cols, int *er, int *ec)
{
    uint64_t srow = 0;      /* біт r — синдром рядка r    */
    uint64_t scol = 0;      /* біт c — синдром стовпця c  */
    int r;

    for (r = 0; r <= rows; r++) {
        srow |= (uint64_t)parity64(w[r]) << r;
        scol ^= w[r];
    }

    assert(parity64(srow) == parity64(scol));   /* та сама тотожність, той самий сенс */

    if (srow == 0 && scol == 0)
        return W2D_CLEAN;

    if (single_bit(srow) && single_bit(scol)) {
        int rr = ctz64(srow), cc = ctz64(scol);
        w[rr] ^= (uint64_t)1 << cc;
        if (er) *er = rr;
        if (ec) *ec = cc;
        return W2D_FIXED;
    }
    return W2D_DETECTED;
}
