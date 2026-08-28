#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>

#define NMEA_MAX_SENTENCE_LEN 84
#define NMEA_MAX_FIELDS       24

typedef enum {
    NMEA_STATE_WAIT_START,
    NMEA_STATE_READ_PAYLOAD,
    NMEA_STATE_READ_CS1,
    NMEA_STATE_READ_CS2,
    NMEA_STATE_WAIT_CR,
    NMEA_STATE_WAIT_LF
} nmea_fsm_state_t;

typedef struct {
    nmea_fsm_state_t state;
    char buffer[NMEA_MAX_SENTENCE_LEN];
    uint8_t buf_idx;
    uint8_t calc_crc;
    uint8_t rx_crc;
    uint32_t sentences_ok;
    uint32_t sentences_err;
} nmea_parser_t;

typedef struct {
    double utc_time;      /* hhmmss.sss */
    double latitude;      /* Десяткові градуси (+N, -S) */
    double longitude;     /* Десяткові градуси (+E, -W) */
    uint8_t fix_quality;  /* 0=Invalid, 1=GPS, 2=DGPS, 4=RTK Fixed, 5=RTK Float */
    uint8_t satellites;   /* Кількість задіяних супутників */
    float hdop;           /* Горизонтальне зниження точності */
    float altitude;       /* Висота над геоїдом (MSL), метри */
    float geoid_sep;      /* Геоїдальне перевищення, метри */
} nmea_gga_data_t;

typedef struct {
    double utc_time;      /* hhmmss.sss */
    bool is_valid;        /* true якщо статус 'A', false якщо 'V' */
    double latitude;      /* Десяткові градуси */
    double longitude;     /* Десяткові градуси */
    float speed_knots;    /* Швидкість у вузлах */
    float speed_mps;      /* Швидкість у м/с */
    float course_deg;     /* Курс над ґрунтом COG у градусах */
    uint32_t date_dmyt;   /* Дата ddmmyy */
    char faa_mode;        /* Режим FAA: 'A', 'D', 'E', 'N' */
} nmea_rmc_data_t;

static inline int hex_digit_to_val(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    return -1;
}

void nmea_parser_init(nmea_parser_t *p) {
    memset(p, 0, sizeof(nmea_parser_t));
    p->state = NMEA_STATE_WAIT_START;
}

/* Потокова обробка одного байта. Повертає true, якщо прийнято повне валідне речення */
bool nmea_parser_feed(nmea_parser_t *p, uint8_t byte, char *out_sentence) {
    if (byte == '$' || byte == '!') {
        p->state = NMEA_STATE_READ_PAYLOAD;
        p->buf_idx = 0;
        p->calc_crc = 0;
        return false;
    }

    switch (p->state) {
        case NMEA_STATE_WAIT_START:
            return false;

        case NMEA_STATE_READ_PAYLOAD:
            if (byte == '*') {
                p->buffer[p->buf_idx] = '\0';
                p->state = NMEA_STATE_READ_CS1;
            } else if (byte == '\r' || byte == '\n') {
                p->state = NMEA_STATE_WAIT_START;
                p->sentences_err++;
            } else {
                if (p->buf_idx < (NMEA_MAX_SENTENCE_LEN - 4)) {
                    p->buffer[p->buf_idx++] = (char)byte;
                    p->calc_crc ^= byte;
                } else {
                    p->state = NMEA_STATE_WAIT_START;
                    p->sentences_err++;
                }
            }
            return false;

        case NMEA_STATE_READ_CS1: {
            int val = hex_digit_to_val((char)byte);
            if (val >= 0) {
                p->rx_crc = (uint8_t)(val << 4);
                p->state = NMEA_STATE_READ_CS2;
            } else {
                p->state = NMEA_STATE_WAIT_START;
                p->sentences_err++;
            }
            return false;
        }

        case NMEA_STATE_READ_CS2: {
            int val = hex_digit_to_val((char)byte);
            if (val >= 0) {
                p->rx_crc |= (uint8_t)val;
                if (p->rx_crc == p->calc_crc) {
                    p->state = NMEA_STATE_WAIT_CR;
                } else {
                    p->state = NMEA_STATE_WAIT_START;
                    p->sentences_err++;
                }
            } else {
                p->state = NMEA_STATE_WAIT_START;
                p->sentences_err++;
            }
            return false;
        }

        case NMEA_STATE_WAIT_CR:
            if (byte == '\r') {
                p->state = NMEA_STATE_WAIT_LF;
            } else if (byte == '\n') {
                p->state = NMEA_STATE_WAIT_START;
                p->sentences_ok++;
                memcpy(out_sentence, p->buffer, p->buf_idx + 1);
                return true;
            } else {
                p->state = NMEA_STATE_WAIT_START;
                p->sentences_err++;
            }
            return false;

        case NMEA_STATE_WAIT_LF:
            p->state = NMEA_STATE_WAIT_START;
            if (byte == '\n') {
                p->sentences_ok++;
                memcpy(out_sentence, p->buffer, p->buf_idx + 1);
                return true;
            }
            p->sentences_err++;
            return false;
    }
    return false;
}

static uint8_t split_fields(char *str, char *fields[], uint8_t max_fields) {
    uint8_t count = 0;
    fields[count++] = str;

    while (*str && count < max_fields) {
        if (*str == ',') {
            *str = '\0';
            fields[count++] = str + 1;
        }
        str++;
    }
    return count;
}

static double parse_coord(const char *val_str, char hemisphere) {
    if (!val_str || !*val_str) return 0.0;
    double raw = atof(val_str);
    int degrees = (int)(raw / 100.0);
    double minutes = raw - (degrees * 100.0);
    double deg = degrees + (minutes / 60.0);
    if (hemisphere == 'S' || hemisphere == 'W') {
        deg = -deg;
    }
    return deg;
}

bool nmea_parse_gga(char *sentence, nmea_gga_data_t *out) {
    char *fields[NMEA_MAX_FIELDS];
    uint8_t num_fields = split_fields(sentence, fields, NMEA_MAX_FIELDS);

    if (num_fields < 10) return false;
    size_t len0 = strlen(fields[0]);
    if (len0 < 3 || strcmp(fields[0] + len0 - 3, "GGA") != 0) {
        return false;
    }

    memset(out, 0, sizeof(nmea_gga_data_t));
    if (*fields[1]) out->utc_time    = atof(fields[1]);
    if (*fields[2] && *fields[3]) out->latitude = parse_coord(fields[2], fields[3][0]);
    if (*fields[4] && *fields[5]) out->longitude = parse_coord(fields[4], fields[5][0]);
    if (*fields[6]) out->fix_quality = (uint8_t)atoi(fields[6]);
    if (*fields[7]) out->satellites  = (uint8_t)atoi(fields[7]);
    if (*fields[8]) out->hdop        = (float)atof(fields[8]);
    if (*fields[9]) out->altitude    = (float)atof(fields[9]);
    if (num_fields > 11 && *fields[11]) out->geoid_sep = (float)atof(fields[11]);

    return true;
}

bool nmea_parse_rmc(char *sentence, nmea_rmc_data_t *out) {
    char *fields[NMEA_MAX_FIELDS];
    uint8_t num_fields = split_fields(sentence, fields, NMEA_MAX_FIELDS);

    if (num_fields < 10) return false;
    size_t len0 = strlen(fields[0]);
    if (len0 < 3 || strcmp(fields[0] + len0 - 3, "RMC") != 0) {
        return false;
    }

    memset(out, 0, sizeof(nmea_rmc_data_t));
    if (*fields[1]) out->utc_time = atof(fields[1]);
    out->is_valid = (fields[2][0] == 'A');
    if (*fields[3] && *fields[4]) out->latitude = parse_coord(fields[3], fields[4][0]);
    if (*fields[5] && *fields[6]) out->longitude = parse_coord(fields[5], fields[6][0]);
    if (*fields[7]) {
        out->speed_knots = (float)atof(fields[7]);
        out->speed_mps = out->speed_knots * 0.51444444f;
    }
    if (*fields[8]) out->course_deg = (float)atof(fields[8]);
    if (*fields[9]) out->date_dmyt = (uint32_t)atoi(fields[9]);
    if (num_fields > 12 && *fields[12]) out->faa_mode = fields[12][0];

    return true;
}

int main(void) {
    nmea_parser_t parser;
    nmea_parser_init(&parser);

    const char stream[] = 
        "NOISE\x1B\x00$GNGGA,123519.00,4807.0382,N,01131.0000,E,1,08,0.9,545.4,M,46.9,M,,*47\r\n"
        "$GNRMC,123519.00,A,4807.0382,N,01131.0000,E,022.4,084.4,230324,003.1,W,A*1D\r\n";

    char sentence[NMEA_MAX_SENTENCE_LEN];
    nmea_gga_data_t gga;
    nmea_rmc_data_t rmc;

    for (size_t i = 0; i < strlen(stream); i++) {
        if (nmea_parser_feed(&parser, (uint8_t)stream[i], sentence)) {
            printf("Прийнято речення: %s\n", sentence);
            char temp_buf[NMEA_MAX_SENTENCE_LEN];
            
            strcpy(temp_buf, sentence);
            if (nmea_parse_gga(temp_buf, &gga)) {
                printf("  [GGA] Широта: %.6f°, Довгота: %.6f°, Висота: %.1f м\n",
                       gga.latitude, gga.longitude, gga.altitude);
            }
            
            strcpy(temp_buf, sentence);
            if (nmea_parse_rmc(temp_buf, &rmc)) {
                printf("  [RMC] Швидкість: %.2f м/с (%.1f вузлів), Курс: %.1f°, Дата: %06u\n",
                       rmc.speed_mps, rmc.speed_knots, rmc.course_deg, rmc.date_dmyt);
            }
        }
    }

    printf("\nПідсумок FSM: Валідних = %u, Помилок = %u\n", 
           parser.sentences_ok, parser.sentences_err);
    return 0;
}
