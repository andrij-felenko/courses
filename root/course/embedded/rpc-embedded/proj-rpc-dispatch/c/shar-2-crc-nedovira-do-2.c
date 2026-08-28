// Порахувати CRC над полями кадру (усе, крім останніх 2 байтів — самого crc).
static uint16_t req_crc(const rpc_req_t *r) {
    return crc16((const uint8_t *)r, sizeof(*r) - sizeof(r->crc));
}
static uint16_t resp_crc(const rpc_resp_t *r) {
    return crc16((const uint8_t *)r, sizeof(*r) - sizeof(r->crc));
}

// Кадр цілий, якщо порахована сума збіглася із записаною.
static bool req_ok(const rpc_req_t *r)  { return req_crc(r)  == r->crc; }
static bool resp_ok(const rpc_resp_t *r){ return resp_crc(r) == r->crc; }
