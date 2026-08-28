static inline int parse_wday_token(const char *p) {
    uint16_t tag = ((uint16_t)p[0] << 8) | (uint16_t)p[1];
    switch (tag) {
        case 0x5355: return 0; /* 'S' 'U' */
        case 0x4D4F: return 1; /* 'M' 'O' */
        case 0x5455: return 2; /* 'T' 'U' */
        case 0x5745: return 3; /* 'W' 'E' */
        case 0x5448: return 4; /* 'T' 'H' */
        case 0x4652: return 5; /* 'F' 'R' */
        case 0x5341: return 6; /* 'S' 'A' */
        default:     return -1;
    }
}
