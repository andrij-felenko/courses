/* C Implementation: Paul Kellet's Pink Noise Filter */
typedef struct {
    double b0, b1, b2, b3, b4, b5, b6;
} PinkNoiseState;

double generate_pink_sample(PinkNoiseState *st, double white_sample) {
    st->b0 = 0.99886 * st->b0 + white_sample * 0.0555179;
    st->b1 = 0.99332 * st->b1 + white_sample * 0.0750759;
    st->b2 = 0.96900 * st->b2 + white_sample * 0.1538520;
    st->b3 = 0.86650 * st->b3 + white_sample * 0.3104856;
    st->b4 = 0.55000 * st->b4 + white_sample * 0.5329522;
    st->b5 = -0.7616 * st->b5 - white_sample * 0.0168980;
    double pink = st->b0 + st->b1 + st->b2 + st->b3 + st->b4 + st->b5 + st->b6 + white_sample * 0.5362;
    st->b6 = white_sample * 0.115926;
    return pink * 0.11; /* Scale to unit variance */
}
