#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <arpa/inet.h>

typedef struct {
    const uint8_t *data;
    size_t len;
    size_t offset;
} BufferReader;

static int read_uint32(BufferReader *r, uint32_t *out) {
    if (r->offset + 4 > r->len) return 0;
    uint32_t val;
    memcpy(&val, r->data + r->offset, 4);
    *out = ntohl(val);
    r->offset += 4;
    return 1;
}

static int read_uint64(BufferReader *r, uint64_t *out) {
    if (r->offset + 8 > r->len) return 0;
    uint32_t high, low;
    memcpy(&high, r->data + r->offset, 4);
    memcpy(&low, r->data + r->offset + 4, 4);
    *out = ((uint64_t)ntohl(high) << 32) | ntohl(low);
    r->offset += 8;
    return 1;
}

static int read_string(BufferReader *r, const char **str_out, uint32_t *len_out) {
    uint32_t length;
    if (!read_uint32(r, &length)) return 0;
    if (r->offset + length > r->len) return 0;
    *str_out = (const char *)(r->data + r->offset);
    *len_out = length;
    r->offset += length;
    return 1;
}

int inspect_ssh_certificate(const uint8_t *raw_cert, size_t cert_len) {
    BufferReader reader = { .data = raw_cert, .len = cert_len, .offset = 0 };

    const char *cert_type_str;
    uint32_t cert_type_len;
    if (!read_string(&reader, &cert_type_str, &cert_type_len)) {
        fprintf(stderr, "Помилка читання типу сертифіката\n");
        return -1;
    }
    printf("Тип сертифіката: %.*s\n", (int)cert_type_len, cert_type_str);

    const char *nonce;
    uint32_t nonce_len;
    if (!read_string(&reader, &nonce, &nonce_len)) return -1;

    const char *pubkey_bytes;
    uint32_t pubkey_len;
    if (!read_string(&reader, &pubkey_bytes, &pubkey_len)) return -1;

    uint64_t serial;
    if (!read_uint64(&reader, &serial)) return -1;
    printf("Серійний номер: %llu\n", (unsigned long long)serial);

    uint32_t cert_kind;
    if (!read_uint32(&reader, &cert_kind)) return -1;
    printf("Призначення: %s (%u)\n", 
           (cert_kind == 1) ? "USER CERTIFICATE" : 
           (cert_kind == 2) ? "HOST CERTIFICATE" : "UNKNOWN", cert_kind);

    const char *key_id;
    uint32_t key_id_len;
    if (!read_string(&reader, &key_id, &key_id_len)) return -1;
    printf("Key ID: %.*s\n", (int)key_id_len, key_id);

    const char *principals_blob;
    uint32_t principals_blob_len;
    if (!read_string(&reader, &principals_blob, &principals_blob_len)) return -1;

    printf("Principals (дозволені облікові записи):\n");
    BufferReader princ_reader = {
        .data = (const uint8_t *)principals_blob,
        .len = principals_blob_len,
        .offset = 0
    };
    while (princ_reader.offset < princ_reader.len) {
        const char *p_str;
        uint32_t p_len;
        if (!read_string(&princ_reader, &p_str, &p_len)) break;
        printf("  - %.*s\n", (int)p_len, p_str);
    }

    uint64_t valid_after, valid_before;
    if (!read_uint64(&reader, &valid_after) || !read_uint64(&reader, &valid_before)) return -1;

    time_t t_after = (time_t)valid_after;
    time_t t_before = (time_t)valid_before;
    char buf_after[64], buf_before[64];
    strftime(buf_after, sizeof(buf_after), "%Y-%m-%d %H:%M:%S UTC", gmtime(&t_after));
    strftime(buf_before, sizeof(buf_before), "%Y-%m-%d %H:%M:%S UTC", gmtime(&t_before));

    printf("Діє з: %s (ts=%llu)\n", buf_after, (unsigned long long)valid_after);
    printf("Діє до: %s (ts=%llu)\n", buf_before, (unsigned long long)valid_before);

    return 0;
}
