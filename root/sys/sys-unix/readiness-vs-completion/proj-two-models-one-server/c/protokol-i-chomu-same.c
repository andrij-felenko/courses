#define HDR      4
#define MAXBODY  (1u << 20)     /* довжина з дроту — вхідні дані, не істина */
#define OUTMAX   (4u << 20)     /* клієнт не читає — не ростемо нескінченно */

struct conn {
    int       fd;
    uint8_t   hdr[HDR];
    unsigned  hdr_n;            /* скільки байтів заголовка вже зібрано */
    uint32_t  need;             /* скільки байтів тіла ще бракує; 0 = чекаємо заголовок */
    uint8_t  *out;              /* відповідь, що збирається й відсилається */
    size_t    out_cap, out_len, out_sent;
};
