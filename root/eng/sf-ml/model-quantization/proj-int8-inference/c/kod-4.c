void dense_s8(const DenseLayerS8 *L, const int8_t *in, int8_t *out)
{
    for (int32_t j = 0; j < L->out_dim; ++j) {
        const int8_t *w = L->W + (int64_t)j * L->in_dim;   /* рядок ваг виходу j */
        int32_t acc = L->bias[j];                          /* bias одразу в int32 */

        for (int32_t i = 0; i < L->in_dim; ++i) {
            /* (активація − zero-point) × вага; кожен доданок — до ±32 640,       */
            /* сума тисяч таких безпечно живе в int32                            */
            acc += (int32_t)((int32_t)in[i] - L->in_zp) * (int32_t)w[i];
        }

        out[j] = requantize(acc, L->M0[j], L->shift[j], L->out_zp);
    }
}
