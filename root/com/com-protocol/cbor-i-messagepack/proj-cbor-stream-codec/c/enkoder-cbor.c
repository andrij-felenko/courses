static cbor_error_t write_byte(cbor_writer_t *w, uint8_t b) {
    if (w->offset >= w->capacity) return CBOR_ERR_BUFFER_OVERFLOW;
    w->data[w->offset++] = b;
    return CBOR_OK;
}

static cbor_error_t write_header(cbor_writer_t *w, uint8_t major, uint64_t val) {
    uint8_t major_bits = major << 5;
    if (val < 24) {
        return write_byte(w, major_bits | (uint8_t)val);
    }
    if (val <= 0xFF) {
        cbor_error_t err = write_byte(w, major_bits | 24);
        if (err != CBOR_OK) return err;
        return write_byte(w, (uint8_t)val);
    }
    if (val <= 0xFFFF) {
        cbor_error_t err = write_byte(w, major_bits | 25);
        if (err != CBOR_OK) return err;
        write_byte(w, (uint8_t)(val >> 8));
        return write_byte(w, (uint8_t)(val & 0xFF));
    }
    if (val <= 0xFFFFFFFF) {
        cbor_error_t err = write_byte(w, major_bits | 26);
        if (err != CBOR_OK) return err;
        for (int i = 3; i >= 0; --i) {
            write_byte(w, (uint8_t)((val >> (i * 8)) & 0xFF));
        }
        return CBOR_OK;
    }
    cbor_error_t err = write_byte(w, major_bits | 27);
    if (err != CBOR_OK) return err;
    for (int i = 7; i >= 0; --i) {
        write_byte(w, (uint8_t)((val >> (i * 8)) & 0xFF));
    }
    return CBOR_OK;
}

cbor_error_t cbor_write_uint(cbor_writer_t *w, uint64_t val) {
    return write_header(w, 0, val);
}

cbor_error_t cbor_write_tstr(cbor_writer_t *w, const char *str, size_t len) {
    cbor_error_t err = write_header(w, 3, len);
    if (err != CBOR_OK) return err;
    if (w->offset + len > w->capacity) return CBOR_ERR_BUFFER_OVERFLOW;
    for (size_t i = 0; i < len; ++i) {
        w->data[w->offset++] = (uint8_t)str[i];
    }
    return CBOR_OK;
}

cbor_error_t cbor_write_bstr(cbor_writer_t *w, const uint8_t *bytes, size_t len) {
    cbor_error_t err = write_header(w, 2, len);
    if (err != CBOR_OK) return err;
    if (w->offset + len > w->capacity) return CBOR_ERR_BUFFER_OVERFLOW;
    for (size_t i = 0; i < len; ++i) {
        w->data[w->offset++] = bytes[i];
    }
    return CBOR_OK;
}

cbor_error_t cbor_write_map_header(cbor_writer_t *w, size_t num_pairs) {
    return write_header(w, 5, num_pairs);
}

cbor_error_t cbor_write_bool(cbor_writer_t *w, bool val) {
    return write_byte(w, (7 << 5) | (val ? 21 : 20));
}
