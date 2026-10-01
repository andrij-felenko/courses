typedef enum {
    KNOCK_NONE = 0,
    KNOCK_WEAK,
    KNOCK_MEDIUM,
    KNOCK_STRONG
} knock_level_t;

#define T_LOW 500
#define T_HIGH 2000
#define HYSTERESIS 50

knock_level_t classify_knock(int amplitude, knock_level_t current_level) {
    if (current_level == KNOCK_NONE || current_level == KNOCK_WEAK) {
        if (amplitude >= T_HIGH + HYSTERESIS) return KNOCK_STRONG;
        if (amplitude >= T_LOW + HYSTERESIS) return KNOCK_MEDIUM;
        if (amplitude >= T_LOW - HYSTERESIS) return KNOCK_WEAK;
        return KNOCK_NONE;
    }
    if (amplitude >= T_HIGH - HYSTERESIS) return KNOCK_STRONG;
    if (amplitude >= T_LOW - HYSTERESIS) return KNOCK_MEDIUM;
    return KNOCK_NONE;
}
