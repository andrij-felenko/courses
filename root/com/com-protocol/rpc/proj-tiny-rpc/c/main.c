#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>

#define RPC_OK 0
#define RPC_ERR_NOT_FOUND 1
#define RPC_ERR_INVALID_ARG 2
#define RPC_ERR_DECODE 3
#define MAX_VARINT_BYTES 10

/* ── 1. Кодек чисел змінної довжини Base-128 Varint ── */
size_t encode_varint(uint64_t value, uint8_t *out) {
    size_t i = 0;
    while (value >= 0x80) {
        out[i++] = (uint8_t)((value & 0x7F) | 0x80);
        value >>= 7;
    }
    out[i++] = (uint8_t)(value & 0x7F);
    return i;
}

bool decode_varint(const uint8_t *buf, size_t len, size_t *offset, uint64_t *val) {
    uint64_t result = 0;
    int shift = 0;
    size_t cur = *offset;

    while (cur < len) {
        uint8_t byte = buf[cur++];
        result |= (uint64_t)(byte & 0x7F) << shift;
        if ((byte & 0x80) == 0) {
            *offset = cur;
            *val = result;
            return true;
        }
        shift += 7;
        if (shift >= 64) return false; /* Захист від переповнення розрядності */
    }
    return false; /* Буфер закінчився раніше термінального байта */
}

/* ── 2. Структура RPC повідомлення ── */
typedef struct {
    uint64_t call_id;
    uint64_t method_id;
    uint64_t status;
    uint8_t  payload[256];
    size_t   payload_len;
} RpcMessage;

size_t serialize_rpc(const RpcMessage *msg, uint8_t *out) {
    size_t off = 0;
    off += encode_varint(msg->call_id, out + off);
    off += encode_varint(msg->method_id, out + off);
    off += encode_varint(msg->status, out + off);
    off += encode_varint(msg->payload_len, out + off);
    memcpy(out + off, msg->payload, msg->payload_len);
    return off + msg->payload_len;
}

bool deserialize_rpc(const uint8_t *buf, size_t len, RpcMessage *msg) {
    size_t off = 0;
    uint64_t plen = 0;
    if (!decode_varint(buf, len, &off, &msg->call_id)) return false;
    if (!decode_varint(buf, len, &off, &msg->method_id)) return false;
    if (!decode_varint(buf, len, &off, &msg->status)) return false;
    if (!decode_varint(buf, len, &off, &plen)) return false;
    if (off + plen > len || plen > sizeof(msg->payload)) return false;
    
    msg->payload_len = (size_t)plen;
    memcpy(msg->payload, buf + off, plen);
    return true;
}

/* ── 3. Серверна логіка та скелетон ── */
typedef uint64_t (*RpcHandler)(const uint8_t *req, size_t req_len, uint8_t *resp, size_t *resp_len);

uint64_t handle_add(const uint8_t *req, size_t req_len, uint8_t *resp, size_t *resp_len) {
    size_t off = 0;
    uint64_t a, b;
    if (!decode_varint(req, req_len, &off, &a) || !decode_varint(req, req_len, &off, &b)) {
        return RPC_ERR_INVALID_ARG;
    }
    uint64_t sum = a + b;
    *resp_len = encode_varint(sum, resp);
    return RPC_OK;
}

void server_dispatch(const uint8_t *in_buf, size_t in_len, uint8_t *out_buf, size_t *out_len) {
    RpcMessage req, resp;
    if (!deserialize_rpc(in_buf, in_len, &req)) {
        *out_len = 0;
        return;
    }

    resp.call_id = req.call_id;
    resp.method_id = req.method_id;
    resp.payload_len = 0;

    if (req.method_id == 1) { /* Метод 1: Add */
        resp.status = handle_add(req.payload, req.payload_len, resp.payload, &resp.payload_len);
    } else {
        resp.status = RPC_ERR_NOT_FOUND;
    }
    *out_len = serialize_rpc(&resp, out_buf);
}

/* ── 4. Клієнтський стаб ── */
bool rpc_client_add(uint64_t a, uint64_t b, uint64_t *result) {
    uint8_t tx_buf[512], rx_buf[512];
    RpcMessage req = { .call_id = 1001, .method_id = 1, .status = RPC_OK };
    
    /* Маршалінг параметрів у тіло запиту */
    req.payload_len = encode_varint(a, req.payload);
    req.payload_len += encode_varint(b, req.payload + req.payload_len);

    size_t tx_len = serialize_rpc(&req, tx_buf);
    size_t rx_len = 0;

    /* Емуляція транспорту через виклик сервера */
    server_dispatch(tx_buf, tx_len, rx_buf, &rx_len);

    /* Демаршалінг відповіді */
    RpcMessage resp;
    if (!deserialize_rpc(rx_buf, rx_len, &resp)) return false;
    if (resp.call_id != req.call_id || resp.status != RPC_OK) return false;

    size_t off = 0;
    return decode_varint(resp.payload, resp.payload_len, &off, result);
}

int main(void) {
    uint64_t res = 0;
    if (rpc_client_add(150, 350, &res)) {
        printf("C RPC Add(150, 350) returned: %llu\n", (unsigned long long)res);
    }
    return 0;
}
