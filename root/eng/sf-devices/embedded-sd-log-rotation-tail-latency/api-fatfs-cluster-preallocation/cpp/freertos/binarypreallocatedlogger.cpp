#include "ff.h"
#include <cstdint>
#include <array>
#include <string_view>

class BinaryPreallocatedLogger {
public:
    static constexpr std::size_t kFileSize = 16 * 1024 * 1024; // 16 MiB
    static constexpr std::size_t kMaxFiles = 4;

    BinaryPreallocatedLogger() = default;

    FRESULT init() {
        for (std::size_t i = 0; i < kMaxFiles; ++i) {
            FIL tmp_file;
            FRESULT fr = f_open(&tmp_file, kFileNames[i].data(), FA_CREATE_ALWAYS | FA_WRITE | FA_READ);
            if (fr != FR_OK) return fr;

            // Створення суцільного ланцюжка кластерів без динамічного розширення
            fr = f_expand(&tmp_file, kFileSize, 1);
            f_close(&tmp_file);
            if (fr != FR_OK) return fr;
        }

        active_file_idx_ = 0;
        write_offset_ = 0;
        return f_open(&active_file_, kFileNames[0].data(), FA_WRITE);
    }

    FRESULT writeRecord(const void* buffer, UINT size) {
        if (write_offset_ + size > kFileSize) {
            rotateToNextFile();
        }

        UINT written = 0;
        FRESULT fr = f_write(&active_file_, buffer, size, &written);
        if (fr == FR_OK) {
            write_offset_ += written;
        }
        return fr;
    }

private:
    void rotateToNextFile() {
        f_sync(&active_file_);
        f_close(&active_file_);

        active_file_idx_ = (active_file_idx_ + 1) % kMaxFiles;
        write_offset_ = 0;

        f_open(&active_file_, kFileNames[active_file_idx_].data(), FA_WRITE);
        f_lseek(&active_file_, 0);
    }

    FIL active_file_{};
    std::size_t active_file_idx_{0};
    std::size_t write_offset_{0};

    static constexpr std::array<std::string_view, kMaxFiles> kFileNames = {
        "0:/log_0.bin",
        "0:/log_1.bin",
        "0:/log_2.bin",
        "0:/log_3.bin"
    };
};
