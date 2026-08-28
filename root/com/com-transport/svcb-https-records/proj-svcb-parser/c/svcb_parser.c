/* svcb_parser.c — Низькорівневий парсер RDATA записів SVCB/HTTPS (RFC 9460) на C */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#if defined(_WIN32)
#include <winsock2.h>
#include <ws2tcpip.h>
#else
#include <arpa/inet.h>
#endif

#define SVCB_KEY_MANDATORY        0
#define SVCB_KEY_ALPN             1
#define SVCB_KEY_NO_DEFAULT_ALPN  2
#define SVCB_KEY_PORT             3
#define SVCB_KEY_IPV4HINT         4
#define SVCB_KEY_ECH              5
#define SVCB_KEY_IPV6HINT         6
#define SVCB_KEY_DOHPATH          7

#define MAX_TARGET_NAME_LEN 256
#define MAX_ALPN_ENTRIES    8
#define MAX_IP_HINTS        8

typedef struct {
    uint16_t priority;
    bool is_alias_mode;
    char target_name[MAX_TARGET_NAME_LEN];
    
    /* Параметри ServiceMode */
    uint16_t port;                      /* За замовчуванням 443 для HTTPS */
    bool no_default_alpn;
    
    char alpn_list[MAX_ALPN_ENTRIES][32];
    size_t alpn_count;
    
    struct in_addr ipv4_hints[MAX_IP_HINTS];
    size_t ipv4_count;
    
    struct in6_addr ipv6_hints[MAX_IP_HINTS];
    size_t ipv6_count;
    
    uint8_t *ech_config;
    size_t ech_len;
    
    uint16_t mandatory_keys[16];
    size_t mandatory_count;
} svcb_record_t;

typedef enum {
    SVCB_OK = 0,
    SVCB_ERR_TRUNCATED,
    SVCB_ERR_INVALID_NAME,
    SVCB_ERR_COMPRESSION_NOT_ALLOWED,
    SVCB_ERR_ALIAS_HAS_PARAMS,
    SVCB_ERR_KEYS_NOT_SORTED,
    SVCB_ERR_DUPLICATE_KEY,
    SVCB_ERR_INVALID_PARAM_LEN,
    SVCB_ERR_MANDATORY_VIOLATION
} svcb_error_t;

/* Читання доменного імені без використання покажчиків стиснення */
static svcb_error_t parse_dns_name(const uint8_t *buf, size_t len, size_t *offset,
                                  char *out_name, size_t max_out) {
    size_t pos = *offset;
    size_t out_pos = 0;
    
    out_name[0] = '\0';
    
    while (pos < len) {
        uint8_t label_len = buf[pos++];
        
        /* Заборона DNS compression pointers (0xC0..0xFF) за RFC 9460 */
        if ((label_len & 0xC0) != 0) {
            return SVCB_ERR_COMPRESSION_NOT_ALLOWED;
        }
        
        if (label_len == 0) {
            /* Нульова мітка завершує ім'я */
            if (out_pos == 0) {
                if (max_out < 2) return SVCB_ERR_INVALID_NAME;
                out_name[0] = '.';
                out_name[1] = '\0';
            } else {
                out_name[out_pos] = '\0';
            }
            *offset = pos;
            return SVCB_OK;
        }
        
        if (pos + label_len > len) {
            return SVCB_ERR_TRUNCATED;
        }
        
        if (out_pos > 0 && out_pos < max_out - 1) {
            out_name[out_pos++] = '.';
        }
        
        if (out_pos + label_len >= max_out) {
            return SVCB_ERR_INVALID_NAME;
        }
        
        memcpy(&out_name[out_pos], &buf[pos], label_len);
        out_pos += label_len;
        pos += label_len;
    }
    
    return SVCB_ERR_TRUNCATED;
}

/* Розбір блоку RDATA запису SVCB/HTTPS */
svcb_error_t svcb_parse_rdata(const uint8_t *rdata, size_t rdata_len, svcb_record_t *rec) {
    if (!rdata || !rec) return SVCB_ERR_TRUNCATED;
    if (rdata_len < 3) return SVCB_ERR_TRUNCATED;
    
    memset(rec, 0, sizeof(*rec));
    rec->port = 443; /* Порт за замовчуванням */
    
    size_t offset = 0;
    
    /* 1. SvcPriority (2 байти, big-endian) */
    rec->priority = (uint16_t)((rdata[offset] << 8) | rdata[offset + 1]);
    offset += 2;
    rec->is_alias_mode = (rec->priority == 0);
    
    /* 2. TargetName */
    svcb_error_t err = parse_dns_name(rdata, rdata_len, &offset,
                                      rec->target_name, sizeof(rec->target_name));
    if (err != SVCB_OK) return err;
    
    /* У режимі AliasMode ціль не може бути "." і параметри заборонені */
    if (rec->is_alias_mode) {
        if (strcmp(rec->target_name, ".") == 0) {
            return SVCB_ERR_INVALID_NAME;
        }
        if (offset < rdata_len) {
            return SVCB_ERR_ALIAS_HAS_PARAMS;
        }
        return SVCB_OK;
    }
    
    /* 3. SvcParams (режим ServiceMode) */
    int32_t last_key = -1;
    
    while (offset < rdata_len) {
        if (offset + 4 > rdata_len) return SVCB_ERR_TRUNCATED;
        
        uint16_t key = (uint16_t)((rdata[offset] << 8) | rdata[offset + 1]);
        uint16_t val_len = (uint16_t)((rdata[offset + 2] << 8) | rdata[offset + 3]);
        offset += 4;
        
        if (offset + val_len > rdata_len) return SVCB_ERR_TRUNCATED;
        
        /* Перевірка строгого сортування ключів (Key[i] > Key[i-1]) */
        if ((int32_t)key <= last_key) {
            return (key == (uint16_t)last_key) ? SVCB_ERR_DUPLICATE_KEY : SVCB_ERR_KEYS_NOT_SORTED;
        }
        last_key = (int32_t)key;
        
        const uint8_t *val = &rdata[offset];
        
        switch (key) {
            case SVCB_KEY_MANDATORY: {
                if (val_len % 2 != 0) return SVCB_ERR_INVALID_PARAM_LEN;
                size_t count = val_len / 2;
                for (size_t i = 0; i < count && rec->mandatory_count < 16; i++) {
                    uint16_t mkey = (uint16_t)((val[i*2] << 8) | val[i*2 + 1]);
                    rec->mandatory_keys[rec->mandatory_count++] = mkey;
                }
                break;
            }
            case SVCB_KEY_ALPN: {
                size_t v_off = 0;
                while (v_off < val_len && rec->alpn_count < MAX_ALPN_ENTRIES) {
                    uint8_t slen = val[v_off++];
                    if (v_off + slen > val_len || slen >= 32) return SVCB_ERR_INVALID_PARAM_LEN;
                    memcpy(rec->alpn_list[rec->alpn_count], &val[v_off], slen);
                    rec->alpn_list[rec->alpn_count][slen] = '\0';
                    rec->alpn_count++;
                    v_off += slen;
                }
                break;
            }
            case SVCB_KEY_NO_DEFAULT_ALPN: {
                if (val_len != 0) return SVCB_ERR_INVALID_PARAM_LEN;
                rec->no_default_alpn = true;
                break;
            }
            case SVCB_KEY_PORT: {
                if (val_len != 2) return SVCB_ERR_INVALID_PARAM_LEN;
                rec->port = (uint16_t)((val[0] << 8) | val[1]);
                break;
            }
            case SVCB_KEY_IPV4HINT: {
                if (val_len % 4 != 0) return SVCB_ERR_INVALID_PARAM_LEN;
                size_t count = val_len / 4;
                for (size_t i = 0; i < count && rec->ipv4_count < MAX_IP_HINTS; i++) {
                    memcpy(&rec->ipv4_hints[rec->ipv4_count++].s_addr, &val[i*4], 4);
                }
                break;
            }
            case SVCB_KEY_IPV6HINT: {
                if (val_len % 16 != 0) return SVCB_ERR_INVALID_PARAM_LEN;
                size_t count = val_len / 16;
                for (size_t i = 0; i < count && rec->ipv6_count < MAX_IP_HINTS; i++) {
                    memcpy(&rec->ipv6_hints[rec->ipv6_count++].s6_addr, &val[i*16], 16);
                }
                break;
            }
            case SVCB_KEY_ECH: {
                rec->ech_config = (uint8_t *)malloc(val_len);
                if (rec->ech_config) {
                    memcpy(rec->ech_config, val, val_len);
                    rec->ech_len = val_len;
                }
                break;
            }
            default:
                /* Невідомі ключі пропускаються, якщо вони не вказані у mandatory */
                break;
        }
        
        offset += val_len;
    }
    
    return SVCB_OK;
}

void svcb_free_record(svcb_record_t *rec) {
    if (rec && rec->ech_config) {
        free(rec->ech_config);
        rec->ech_config = NULL;
        rec->ech_len = 0;
    }
}
