#include <cstdint>
#include <cstdio>
#include <cstddef>
#include <string>

// Таблиця відображеного полінома CRC-32 — та сама, що в zip і PNG.
static const uint32_t *crcTable()
{
    static uint32_t table[256];
    static bool built = false;
    if (!built) {
        for (uint32_t i = 0; i < 256; ++i) {
            uint32_t k = i;
            for (int j = 0; j < 8; ++j)
                k = (k & 1u) ? ((k >> 1) ^ 0xEDB88320u) : (k >> 1);
            table[i] = k;
        }
        built = true;
    }
    return table;
}

uint32_t metadataCrc32(const uint8_t *data, size_t len)
{
    const uint32_t *table = crcTable();
    uint32_t crc = 0;                    // zip почав би з 0xFFFFFFFF
    for (size_t i = 0; i < len; ++i)
        crc = (crc >> 8) ^ table[(crc & 0xFFu) ^ data[i]];
    return crc;                          // zip завершив би ^ 0xFFFFFFFF
}

std::string cacheTag(int metaType, uint32_t crc, bool translation)
{
    char buf[32];
    std::snprintf(buf, sizeof buf, "%08x_%02i_%i",
                  static_cast<unsigned>(crc), metaType, translation ? 1 : 0);
    return buf;
}
