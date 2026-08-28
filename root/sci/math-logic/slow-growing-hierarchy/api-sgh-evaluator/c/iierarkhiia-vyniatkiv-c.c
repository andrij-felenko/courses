/* У C API помилки обробляються через повернення кодів SghStatus */
const char *sgh_status_to_string(SghStatus status) {
    switch (status) {
        case SGH_OK: return "OK";
        case SGH_ERR_NULL_PTR: return "Null pointer argument";
        case SGH_ERR_OVERFLOW: return "Arithmetic integer overflow";
        case SGH_ERR_INVALID_ORDINAL: return "Invalid Cantor normal form";
        case SGH_ERR_OUT_OF_MEMORY: return "Out of memory";
        case SGH_ERR_PARSE_SYNTAX: return "Syntax parsing error";
        case SGH_ERR_NOT_A_LIMIT: return "Not a limit ordinal";
        default: return "Unknown error";
    }
}
