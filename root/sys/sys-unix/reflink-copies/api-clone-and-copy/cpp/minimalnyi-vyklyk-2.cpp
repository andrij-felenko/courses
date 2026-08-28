#include <cstdint>
#include <vector>
#include <cstddef>
#include <sys/ioctl.h>
#include <linux/fs.h>
#include <system_error>

// Зливає один діапазон джерела з декількома призначеннями.
// Повертає кількість призначень, де байти дійсно збіглися й були злиті.
int dedupe_range(int src_fd, std::uint64_t off, std::uint64_t len,
                 const std::vector<int>& dst_fds,
                 const std::vector<std::uint64_t>& dst_offs)
{
    const std::size_t n = dst_fds.size();
    const std::size_t sz = sizeof(file_dedupe_range)
                         + n * sizeof(file_dedupe_range_info);

    std::vector<std::byte> buf(sz, std::byte{0});
    auto* arg = reinterpret_cast<file_dedupe_range*>(buf.data());

    arg->src_offset = off;
    arg->src_length = len;
    arg->dest_count = static_cast<std::uint16_t>(n);
    for (std::size_t i = 0; i < n; ++i) {
        arg->info[i].dest_fd = dst_fds[i];
        arg->info[i].dest_offset = dst_offs[i];
    }

    if (::ioctl(src_fd, FIDEDUPERANGE, arg) != 0) {
        throw std::system_error(errno, std::generic_category(), "FIDEDUPERANGE ioctl failed");
    }

    int same = 0;
    for (std::size_t i = 0; i < n; ++i) {
        if (arg->info[i].status == FILE_DEDUPE_RANGE_SAME && arg->info[i].bytes_deduped > 0) {
            ++same;
        }
    }
    return same;
}
