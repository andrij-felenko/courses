#include <ublksrv.h>
#include <algorithm>
#include <cerrno>
#include <iostream>
#include <vector>
#include <memory>
#include <span>
#include <cstdint>

class UblkRamdiskTarget {
public:
    explicit UblkRamdiskTarget(std::size_t size_bytes)
        : storage_(size_bytes, 0) {}

    int handle_io(const struct ublksrv_queue* q, const struct ublk_io_data* data) noexcept {
        const auto* desc = data->desc;
        const uint32_t op = ublksrv_get_op(desc);
        const uint64_t offset = ublksrv_get_sector(desc) << 9;
        const uint32_t nr_bytes = ublksrv_get_nr_bytes(desc);

        if (offset + nr_bytes > storage_.size()) {
            ublksrv_complete_io(q, data, -EIO);
            return 0;
        }

        auto* io_buf = static_cast<std::byte*>(ublksrv_get_io_buf(q, data));
        std::span<std::byte> buffer(io_buf, nr_bytes);
        std::span<std::byte> storage_span(reinterpret_cast<std::byte*>(storage_.data()) + offset, nr_bytes);

        if (op == UBLK_IO_OP_READ) {
            std::copy(storage_span.begin(), storage_span.end(), buffer.begin());
        } else if (op == UBLK_IO_OP_WRITE) {
            std::copy(buffer.begin(), buffer.end(), storage_span.begin());
        }

        ublksrv_complete_io(q, data, nr_bytes);
        return 0;
    }

    [[nodiscard]] std::size_t size() const noexcept { return storage_.size(); }

private:
    std::vector<uint8_t> storage_;
};

int main() {
    constexpr std::size_t disk_size = 64 * 1024 * 1024; // 64 MiB
    auto target = std::make_unique<UblkRamdiskTarget>(disk_size);

    auto io_callback = [](const struct ublksrv_queue* q, const struct ublk_io_data* data) -> int {
        auto* instance = static_cast<UblkRamdiskTarget*>(ublksrv_get_queue_app_data(q));
        return instance->handle_io(q, data);
    };

    struct ublksrv_dev* dev = ublksrv_dev_init(0, io_callback, target.get());
    if (!dev) {
        std::cerr << "Помилка ініціалізації ublk пристрою у C++" << std::endl;
        return 1;
    }

    std::cout << "ublk C++ RAM-диск запущено: " << target->size() / (1024 * 1024) << " MiB" << std::endl;
    ublksrv_start_dev(dev);

    ublksrv_dev_deinit(dev);
    return 0;
}
