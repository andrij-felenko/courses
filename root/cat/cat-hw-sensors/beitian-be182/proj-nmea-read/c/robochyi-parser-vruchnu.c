// Розбір рядка GGA на координати. Повертає 1, якщо є дійсний fix.
// УВАГА: strtok псує вхідний рядок — передавайте копію, не оригінал буфера.
#include <stdio.h>

typedef struct { double lat, lon; int sats; int fix; } gga_t;

int parse_gga(char *line, gga_t *out) {        // line — змінна копія!
    if (!nmea_checksum_ok(line)) return 0;     // спершу контрольна сума
    // тип рядка — після коми стоїть, тому дивимось перші літери
    if (strncmp(line + 3, "GGA", 3) != 0) return 0;   // "$GPGGA" → зсув 3

    char *lat = NULL, *ns = NULL, *lon = NULL, *ew = NULL, *fix = NULL, *sat = NULL;
    int f = 0;
    for (char *tok = strtok(line, ","); tok; tok = strtok(NULL, ","), f++) {
        switch (f) {
            case 2: lat = tok; break;   // широта  ddmm.mmmm
            case 3: ns  = tok; break;   // N / S
            case 4: lon = tok; break;   // довгота dddmm.mmmm
            case 5: ew  = tok; break;   // E / W
            case 6: fix = tok; break;   // якість fix
            case 7: sat = tok; break;   // супутників
        }
    }
    out->fix  = fix ? atoi(fix) : 0;
    if (out->fix == 0) return 0;                // нема fix — координатам не вірити
    out->lat  = nmea_to_degrees(lat, ns ? ns[0] : 'N', 2);
    out->lon  = nmea_to_degrees(lon, ew ? ew[0] : 'E', 3);
    out->sats = sat ? atoi(sat) : 0;
    return 1;
}
