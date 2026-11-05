#include "ff.h"
#include <cstdint>
#include <cstring>

class PreallocatedLogFile {
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

    PreallocatedLogFile() = default;

    FRESULT initialize(const char* path, FSIZE_t required_bytes) {
        FRESULT res = f_open(&file_handle_, path, FA_READ | FA_WRITE | FA_OPEN_ALWAYS);
        if (res != FR_OK) {
            return res;
        }

        if (f_size(&file_handle_) < required_bytes) {
            res = f_lseek(&file_handle_, 0);
            if (res != FR_OK) {
                f_close(&file_handle_);
                return res;
            }

            /* Запит суцільного предвиділення кластерів у FatFs */
            res = f_expand(&file_handle_, required_bytes, 1);
            if (res != FR_OK) {
                f_close(&file_handle_);
                return res;
            }

            Header header{};
            header.magic = kHeaderMagic;
            header.version = 1U;
            header.write_offset = sizeof(Header);
            header.read_offset = sizeof(Header);

            UINT written = 0;
            res = f_write(&file_handle_, &header, sizeof(header), &written);
            if (res != FR_OK || written != sizeof(header)) {
                f_close(&file_handle_);
                return res;
            }

            res = f_sync(&file_handle_);
            if (res != FR_OK) {
                f_close(&file_handle_);
                return res;
            }
        }

        is_initialized_ = true;
        return f_lseek(&file_handle_, sizeof(Header));
    }

    FIL* get_file_ptr() { return &file_handle_; }
    bool is_initialized() const { return is_initialized_; }

    ~PreallocatedLogFile() {
        if (is_initialized_) {
            f_close(&file_handle_);
        }
    }

private:
    FIL file_handle_{};
    bool is_initialized_{false};
};
