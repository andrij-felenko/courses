typedef enum {
    PT100_OK = 0,
    PT100_ERROR_SHORT_CIRCUIT,
    PT100_ERROR_OPEN_CIRCUIT
} pt100_status_t;

pt100_status_t pt100_validate_resistance(float resistance_ohm) {
    if (resistance_ohm < 15.0f) {
        return PT100_ERROR_SHORT_CIRCUIT;
    }
    if (resistance_ohm > 400.0f) {
        return PT100_ERROR_OPEN_CIRCUIT;
    }
    return PT100_OK;
}
