#include "report.h"

#include <stddef.h>

void fm_report_ack(const fm_reporter_t *r, uint16_t command, uint8_t result)
{
    if (r && r->command_ack) {
        r->command_ack(r->ctx, command, result);
    }
}

void fm_report_text(const fm_reporter_t *r, uint8_t severity, const char *text)
{
    if (r && r->statustext && text) {
        r->statustext(r->ctx, severity, text);
    }
}

void fm_report_tone(const fm_reporter_t *r, fm_tone_t tone)
{
    if (r && r->tone) {
        r->tone(r->ctx, tone);
    }
}
