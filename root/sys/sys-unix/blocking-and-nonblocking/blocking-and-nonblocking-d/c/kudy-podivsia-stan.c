enum phase { WANT_HEADER, WANT_BODY, WANT_FLUSH };

struct conn {
    int         fd;
    enum phase  phase;
    char        in[4096];
    size_t      in_len;      /* скільки вже накопичено */
    size_t      body_left;   /* скільки байтів тіла ще бракує */
    char       *out;
    size_t      out_len, out_off;
};
