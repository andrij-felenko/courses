#include <gtest/gtest.h>

TEST(StatxTest, DirectIOAlignmentCheck) {
    auto info = fs_inspect::StatxInfo::fetch("/tmp/test_file.bin", STATX_DIOALIGN);
    if (info.has_field(STATX_DIOALIGN)) {
        uint32_t align = info.dio_mem_align();
        // Нуль означає, що файл узагалі не підтримує O_DIRECT;
        // інакше вирівнювання зобов'язане бути степенем двійки
        if (align != 0) {
            EXPECT_TRUE((align & (align - 1)) == 0);
        }
    }
}
