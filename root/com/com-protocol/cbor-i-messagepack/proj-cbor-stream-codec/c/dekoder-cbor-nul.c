static cbor_error_t read_bytes(cbor_reader_t *r, void *dest, size_t n) {
    if (r->offset + n > r->size) {
        return CBOR_ERR_UNEXPECTED_EOF;
    }
    const uint8_t *src = r->data + r->offset;
    uint8_t *d = (uint8_t *)dest;
    for (size_t i = 0; i < n; ++i) {
        d[i] = src[i];
    }
    r->offset += n;
    return CBOR_OK;
}

static cbor_error_t read_uint_payload(cbor_reader_t *r, uint8_t additional_info, uint64_t *val) {
    if (additional_info < 24) {
        *val = additional_info;
        return CBOR_OK;
    }
    if (additional_info == 24) {
        uint8_t b8;
        cbor_error_t err = read_bytes(r, &b8, 1);
        if (err != CBOR_OK) return err;
        *val = b8;
        return CBOR_OK;
    }
    if (additional_info == 25) {
        uint8_t b[2];
        cbor_error_t err = read_bytes(r, b, 2);
        if (err != CBOR_OK) return err;
        *val = ((uint64_t)b[0] << 8) | (uint64_t)b[1];
        return CBOR_OK;
    }
    if (additional_info == 26) {
        uint8_t b[4];
        cbor_error_t err = read_bytes(r, b, 4);
        if (err != CBOR_OK) return err;
        *val = ((uint64_t)b[0] << 24) | ((uint64_t)b[1] << 16) |
               ((uint64_t)b[2] << 8)  | (uint64_t)b[3];
        return CBOR_OK;
    }
    if (additional_info == 27) {
        uint8_t b[8];
        cbor_error_t err = read_bytes(r, b, 8);
        if (err != CBOR_OK) return err;
        *val = ((uint64_t)b[0] << 56) | ((uint64_t)b[1] << 48) |
               ((uint64_t)b[2] << 40) | ((uint64_t)b[3] << 32) |
               ((uint64_t)b[4] << 24) | ((uint64_t)b[5] << 16) |
               ((uint64_t)b[6] << 8)  | (uint64_t)b[7];
        return CBOR_OK;
    }
    return CBOR_ERR_INVALID_HEADER;
}

cbor_error_t cbor_read_next(cbor_reader_t *r, cbor_value_t *out) {
    if (r->offset >= r->size) {
        return CBOR_ERR_UNEXPECTED_EOF;
    }
    uint8_t initial_byte = r->data[r->offset++];
    uint8_t major = initial_byte >> 5;
    uint8_t info = initial_byte & 0x1F;

    uint64_t val = 0;
    cbor_error_t err;

    switch (major) {
        case 0: // Unsigned Integer
            err = read_uint_payload(r, info, &val);
            if (err != CBOR_OK) return err;
            out->type = CBOR_TYPE_UINT;
            out->as.uint_val = val;
            return CBOR_OK;

        case 1: // Negative Integer (-1 - val)
            err = read_uint_payload(r, info, &val);
            if (err != CBOR_OK) return err;
            out->type = CBOR_TYPE_NINT;
            out->as.nint_val = -1 - (int64_t)val;
            return CBOR_OK;

        case 2: // Byte String (Zero-Copy)
        case 3: // Text String (Zero-Copy)
            err = read_uint_payload(r, info, &val);
            if (err != CBOR_OK) return err;
            if (r->offset + val > r->size) return CBOR_ERR_UNEXPECTED_EOF;
            out->type = (major == 2) ? CBOR_TYPE_BSTR : CBOR_TYPE_TSTR;
            out->as.slice.ptr = r->data + r->offset;
            out->as.slice.len = (size_t)val;
            r->offset += (size_t)val;
            return CBOR_OK;

        case 4: // Array Header
            err = read_uint_payload(r, info, &val);
            if (err != CBOR_OK) return err;
            out->type = CBOR_TYPE_ARRAY;
            out->as.container_len = (size_t)val;
            return CBOR_OK;

        case 5: // Map Header (pairs count)
            err = read_uint_payload(r, info, &val);
            if (err != CBOR_OK) return err;
            out->type = CBOR_TYPE_MAP;
            out->as.container_len = (size_t)val;
            return CBOR_OK;

        case 6: // Semantic Tag
            err = read_uint_payload(r, info, &val);
            if (err != CBOR_OK) return err;
            out->type = CBOR_TYPE_TAG;
            out->as.tag_val = val;
            return CBOR_OK;

        case 7: // Simple / Floats
            if (info == 20 || info == 21) {
                out->type = CBOR_TYPE_BOOL;
                out->as.bool_val = (info == 21);
                return CBOR_OK;
            }
            if (info == 22) {
                out->type = CBOR_TYPE_NULL;
                return CBOR_OK;
            }
            if (info == 26) { // IEEE 754 Float32
                uint32_t raw;
                err = read_uint_payload(r, 26, &val);
                if (err != CBOR_OK) return err;
                raw = (uint32_t)val;
                union { uint32_t u; float f; } conv;
                conv.u = raw;
                out->type = CBOR_TYPE_FLOAT32;
                out->as.float_val = conv.f;
                return CBOR_OK;
            }
            return CBOR_ERR_UNSUPPORTED_TYPE;

        default:
            return CBOR_ERR_UNSUPPORTED_TYPE;
    }
}
