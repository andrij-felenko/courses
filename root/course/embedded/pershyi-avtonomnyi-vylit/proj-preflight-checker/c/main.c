#include <errno.h>
#include <stdio.h>
#include <string.h>

#include "preflight.h"
#include "telemetry.h"

/* Передпольотний чекер: читає зліпок телеметрії (аргумент або stdin),
   проганяє його крізь шість бар'єрів і друкує вердикт.

   Коди повернення — на них спирається пусковий скрипт польотної групи:
     0 — GO, дозвіл на ARM;
     1 — NO-GO, є щонайменше одне блокування;
     2 — зліпок непридатний, вердикту немає взагалі.
   Третій код окремий навмисно: «не зміг перевірити» — це не «перевірив і
   дозволив», і плутати їх у скрипті означає злетіти наосліп. */
int main(int argc, char **argv)
{
    if (argc > 2) {
        fprintf(stderr, "вжиток: %s [зліпок-телеметрії.txt]\n", argv[0]);
        return 2;
    }

    FILE *in = stdin;
    if (argc == 2 && strcmp(argv[1], "-") != 0) {
        in = fopen(argv[1], "r");
        if (in == NULL) {
            fprintf(stderr, "не вдалося відкрити '%s': %s\n", argv[1], strerror(errno));
            return 2;
        }
    }

    VehicleTelemetryState telemetry;
    char err[224];
    int rc = telemetry_parse(in, &telemetry, err, sizeof err);

    if (in != stdin) {
        fclose(in);
    }

    if (rc != 0) {
        fprintf(stderr, "зліпок телеметрії непридатний: %s\n", err);
        fprintf(stderr, "вердикт не винесено — армінг заборонено\n");
        return 2;
    }

    PreflightReport report = run_preflight_validation(&telemetry);
    print_report(&report, stdout);

    return report.is_go ? 0 : 1;
}
