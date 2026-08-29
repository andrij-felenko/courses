/* main.c — цикл вузла: прокинувся, зміряв, вистрілив датаграму, заснув.
 *
 * Збірка:
 *   cc -std=c11 -O2 -Wall -Wextra -o node    main.c frame.c uplink.c
 *   cc -std=c11 -O2 -Wall -Wextra -o gateway gateway.c frame.c
 *
 * Запуск:  ./gateway 9000  і в іншому терміналі  ./node 127.0.0.1 9000
 *
 * На мікроконтролері замість main() тут була б функція, яку викликає
 * пробудження від RTC, а замість повернення з main() — виклик сну. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

#include "uplink.h"

#define SPOOL_PATH "node.spool"
#define SEQ_PATH   "node.seq"

/* Номер кадру мусить пережити перезавантаження, інакше після скидання
 * вузол почне з нуля і сервер вважатиме свіжі виміри дублікатами.
 * У прошивці це запис у NVS, тут — чотири байти у файлі. */
static uint16_t seq_load(void)
{
    FILE *f = fopen(SEQ_PATH, "rb");
    if (f == NULL) {
        return 0;
    }
    uint16_t seq = 0;
    if (fread(&seq, sizeof seq, 1, f) != 1) {
        seq = 0;
    }
    fclose(f);
    return seq;
}

static void seq_store(uint16_t seq)
{
    FILE *f = fopen(SEQ_PATH, "wb");
    if (f == NULL) {
        fprintf(stderr, "node: лічильник не збережено\n");
        return;
    }
    fwrite(&seq, sizeof seq, 1, f);
    fclose(f);
}

/* У прошивці тут читання SHT4x по I²C і напруги батареї з АЦП.
 * Щоб приклад ішов на ПК, числа беремо детерміновані, але правдоподібні. */
static void measure(sensor_sample_t *sample)
{
    time_t now = time(NULL);
    long minute = (long)(now % 3600) / 60;          /* 0..59 */

    sample->timestamp   = (uint32_t)now;
    sample->temperature = (int16_t)(1800 + minute * 10);   /* 18.00..27.90 °C */
    sample->humidity    = (uint16_t)(4000 + (59 - minute) * 20);
    sample->vbat_mv     = (uint16_t)(3000 - (now % 600) / 10);
}

int main(int argc, char **argv)
{
    const char *host = (argc > 1) ? argv[1] : "127.0.0.1";
    const char *port = (argc > 2) ? argv[2] : "9000";

    uplink_t up;
    if (uplink_open(&up, host, port, SPOOL_PATH, seq_load()) != 0) {
        return 1;
    }

    /* Спершу віддаємо борги: модем уже увімкнений, і кожен відкладений кадр
     * коштує тепер лише свої 16 байтів, а не окремого пробудження. */
    int replayed = uplink_flush_spool(&up);
    if (replayed > 0) {
        printf("віддано зі спулу: %d кадр(ів)\n", replayed);
    }

    sensor_sample_t sample;
    measure(&sample);

    int rc = uplink_send(&up, &sample);
    if (rc == 0) {
        printf("кадр #%u підтверджено: %d.%02d °C, %u.%02u %%, %u мВ\n",
               (unsigned)(up.seq - 1),
               sample.temperature / 100, (sample.temperature % 100 + 100) % 100,
               sample.humidity / 100, sample.humidity % 100,
               sample.vbat_mv);
    } else {
        printf("кадр #%u відкладено у спул\n", (unsigned)(up.seq - 1));
    }

    seq_store(up.seq);

    /* Головне число цієї теми: скільки мілісекунд передавач мусив жити.
     * Для HTTPS-сеансу з нуля тут було б понад тисячу. */
    printf("передавач був потрібен %lld мс\n", up.tx_ms);

    uplink_close(&up);
    return (rc == 0) ? 0 : 1;
}
