// Вигляд структури <linux/fiemap.h> у C++
struct fiemap {
    uint64_t fm_start;          // з якого зсуву питаємо        — вхід
    uint64_t fm_length;         // яку довжину хочемо покрити   — вхід
    uint32_t fm_flags;          // FIEMAP_FLAG_*            — вхід/вихід
    uint32_t fm_mapped_extents; // скільки записів заповнено    — вихід
    uint32_t fm_extent_count;   // скільки слотів ми дали       — вхід
    uint32_t fm_reserved;
    fiemap_extent fm_extents[]; // гнучкий масив екстентів
};
