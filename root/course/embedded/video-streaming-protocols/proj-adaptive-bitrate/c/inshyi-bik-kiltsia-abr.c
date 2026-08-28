// Сходинки якості з маніфесту (HLS/DASH), від нижчої до вищої, біт/с.
static const uint32_t LADDER[] = {
    400000, 800000, 1500000, 3000000, 6000000   // 480p … 1080p
};
static const int LADDER_N = sizeof(LADDER) / sizeof(LADDER[0]);

// Вибір сходинки під виміряну пропускну.
//   segment_bytes — розмір щойно завантаженого сегмента
//   download_ms   — скільки тривало його завантаження
int abr_pick_rendition(uint32_t segment_bytes, uint32_t download_ms)
{
    // виміряна пропускна = байти·8 / час  (біт/с); бережемось ділення на нуль
    if (download_ms == 0) download_ms = 1;
    uint32_t measured_bps =
        (uint32_t)(((uint64_t)segment_bytes * 8u * 1000u) / download_ms);

    // safety factor 0.8: лишаємо 20% запасу на коливання
    uint32_t budget = (uint32_t)(((uint64_t)measured_bps * 80u) / 100u);

    // найвища сходинка, що влазить у бюджет (мінімум — найнижча)
    int pick = 0;
    for (int i = 0; i < LADDER_N; i++) {
        if (LADDER[i] <= budget) pick = i;
    }
    return pick;
}
