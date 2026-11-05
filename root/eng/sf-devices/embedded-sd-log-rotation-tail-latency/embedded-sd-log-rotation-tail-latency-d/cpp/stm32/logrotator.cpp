#include "ff.h"
#include <cstdint>
#include <cstring>

class LogRotator {
public:
    static constexpr uint32_t kSectorSize = 512U;
    static constexpr uint32_t kHeaderMagic = 0x4C4F4752U;

    struct alignas(512) Header {
        uint32_t magic;
        uint32_t version;
        uint32_t write_offset;
        uint32_t read_offset;
        uint32_t total_records;
        uint32_t crc32;
        uint8_t  padding[kSectorSize - 24U];
    };

    LogRotator() = default;

    FRESULT open(const char* path, uint32_t total_file_size) {
        FRESULT res = f_open(&file_, path, FA_READ | FA_WRITE | FA_OPEN_EXISTING);
        if (res != FR_OK) return res;

        UINT read_bytes = 0;
        res = f_read(&file_, &header_, sizeof(Header), &read_bytes);
        if (res != FR_OK || read_bytes != sizeof(Header) || header_.magic != kHeaderMagic) {
            f_close(&file_);
            return FR_CORRUPT;
        }

        total_file_size_ = total_file_size;
        data_start_offset_ = sizeof(Header);
        is_open_ = true;
        return FR_OK;
    }

    FRESULT write_record(const void* data, uint32_t data_len) {
        if (!is_open_ || !data || data_len == 0) return FR_INVALID_PARAMETER;

        uint32_t target_offset = header_.write_offset;
        if (target_offset + data_len > total_file_size_) {
            target_offset = data_start_offset_;
        }

        FRESULT res = f_lseek(&file_, target_offset);
        if (res != FR_OK) return res;

        UINT written = 0;
        res = f_write(&file_, data, data_len, &written);
        if (res != FR_OK || written != data_len) return res;

        header_.write_offset = target_offset + data_len;
        header_.total_records++;

        if ((header_.total_records % 100U) == 0U) {
            sync_header();
        }

        return FR_OK;
    }

    FRESULT sync_header() {
        if (!is_open_) return FR_NOT_READY;
        FRESULT res = f_lseek(&file_, 0);
        if (res != FR_OK) return res;

        UINT written = 0;
        res = f_write(&file_, &header_, sizeof(Header), &written);
        if (res != FR_OK || written != sizeof(Header)) return res;

        return f_sync(&file_);
    }

    ~LogRotator() {
        if (is_open_) {
            sync_header();
            f_close(&file_);
        }
    }

private:
    FIL      file_{};
    Header   header_{};
    uint32_t data_start_offset_{sizeof(Header)};
    uint32_t total_file_size_{0};
    bool     is_open_{false};
};
