enum KnockLevel { KNOCK_NONE, KNOCK_WEAK, KNOCK_MEDIUM, KNOCK_STRONG };

const int T_LOW = 150;
const int T_HIGH = 600;
const int HYSTERESIS = 20;

KnockLevel classifyKnock(int amplitude, KnockLevel currentLevel) {
    if (currentLevel == KNOCK_NONE || currentLevel == KNOCK_WEAK) {
        if (amplitude >= T_HIGH + HYSTERESIS) return KNOCK_STRONG;
        if (amplitude >= T_LOW + HYSTERESIS) return KNOCK_MEDIUM;
        if (amplitude >= T_LOW - HYSTERESIS) return KNOCK_WEAK;
        return KNOCK_NONE;
    }
    if (amplitude >= T_HIGH - HYSTERESIS) return KNOCK_STRONG;
    if (amplitude >= T_LOW - HYSTERESIS) return KNOCK_MEDIUM;
    return KNOCK_NONE;
}
