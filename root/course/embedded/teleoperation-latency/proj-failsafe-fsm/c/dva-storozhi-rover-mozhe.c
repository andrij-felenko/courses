// Оновлюється двома лічильниками тиші: uplink (команди від пульта)
// і downlink (підтвердження від пульта, що він нас чує/бачить).
// Тривога — за ГІРШИМ каналом: досить одному замовкнути.
static uint32_t fs_worst_silence(uint32_t uplink_silent_ms,
                                 uint32_t downlink_silent_ms)
{
    return (uplink_silent_ms > downlink_silent_ms)
             ? uplink_silent_ms
             : downlink_silent_ms;
}
