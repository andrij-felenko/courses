#include <mavlink.h>          /* c_library_v2, зібрана з XML-опису діалекту мережі */
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#define NCHAN         3       /* 0 — UART, 1 — USB, 2 — UDP.                     */
                              /* MAVLINK_COMM_NUM_BUFFERS мусить бути ≥ NCHAN:   */
                              /* у кожного каналу свій стан збирання кадру.      */
#define ROUTE_MAX     24
#define ROUTE_TTL_MS  30000u  /* чому саме стільки — наприкінці */

typedef struct {
    uint8_t  sysid, compid;   /* адреса вузла — пара, не одне число */
    uint8_t  chan;            /* канал, на якому його чули          */
    uint32_t seen_ms;         /* коли чули востаннє                 */
} route_t;

static route_t routes[ROUTE_MAX];
static uint8_t route_n;

/* Єдина зовнішня залежність усього моста. */
extern void chan_write(uint8_t chan, const uint8_t *buf, uint16_t len);

static bool fresh(const route_t *r, uint32_t now)
{
    return (uint32_t)(now - r->seen_ms) <= ROUTE_TTL_MS;
}
