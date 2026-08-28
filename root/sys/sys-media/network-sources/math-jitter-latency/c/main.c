#include <stdint.h>
#include <stddef.h>

#define BINW    32     /* крок кошика, такти 90 кГц: 32 такти = 0.356 мс   */
#define NBIN  1024     /* охоплення разом із ZERO: від −22.8 до +341 мс    */
#define ZERO    64     /* кошик, у який лягає проліт першого пакета        */

struct delay_stats {
    uint32_t ref;          /* проліт першого пакета — довільна точка відліку */
    uint32_t prev;         /* проліт попереднього пакета                     */
    int      started;
    double   jitter;       /* J у тактах — те саме число, що йде в RTCP      */
    uint64_t hist[NBIN];
    uint64_t under, over;  /* усе, що не влізло в гістограму                 */
};

/* arrival — показ локального годинника, переведений у такти шкали RTP;
   rtp_ts  — мітка часу з заголовка пакета.                              */
void on_packet(struct delay_stats *s, uint32_t arrival, uint32_t rtp_ts)
{
    uint32_t transit = arrival - rtp_ts;   /* зсув годинників іще всередині */

    if (!s->started) {
        s->started = 1;
        s->ref = transit;
        s->prev = transit;
    }

    int32_t d = (int32_t)(transit - s->prev);   /* а тут зсув скоротився */
    s->prev = transit;
    if (d < 0) d = -d;
    s->jitter += ((double)d - s->jitter) / 16.0;

    int32_t off = (int32_t)(transit - s->ref);  /* може бути й від'ємним */
    int32_t bin = ZERO + (off >= 0 ? off / BINW : (off - BINW + 1) / BINW);

    if      (bin < 0)     s->under++;
    else if (bin >= NBIN) s->over++;
    else                  s->hist[bin]++;
}

/* Частка пакетів, що спізнилися більш ніж на window тактів понад підлогу.
   under > 0 означає, що підлога вийшла за гістограму: розширюй охоплення. */
double late_fraction(const struct delay_stats *s, int32_t window)
{
    uint64_t total = s->under + s->over;
    size_t i, floor_bin = 0, edge;

    for (i = 0; i < NBIN; i++)
        total += s->hist[i];
    while (floor_bin < NBIN && s->hist[floor_bin] == 0)
        floor_bin++;

    edge = floor_bin + (size_t)(window / BINW);
    uint64_t late = s->over;
    for (i = edge; i < NBIN; i++)
        late += s->hist[i];

    return total ? (double)late / (double)total : 0.0;
}
