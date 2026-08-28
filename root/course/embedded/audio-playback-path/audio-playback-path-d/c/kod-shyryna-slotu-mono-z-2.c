/* зробити зі списку моно-відліків стерео-буфер: кожен відлік — у Л і П */
void mono_to_stereo(const int16_t *mono, int16_t *stereo, size_t n) {
    for (size_t i = 0; i < n; i++) {
        stereo[2*i + 0] = mono[i];   /* лівий слот  */
        stereo[2*i + 1] = mono[i];   /* правий слот */
    }
}

/* віддати блок: виклик блокує, доки DMA не забере його в кільце */
size_t written;
i2s_channel_write(tx_chan, stereo, n * 2 * sizeof(int16_t),
                  &written, portMAX_DELAY);
