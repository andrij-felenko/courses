#include <sys/uio.h>
#include <array>
#include <string_view>

std::uint32_t write_id = reg.write_index;
std::string_view url = "/api/v1/resource";

std::array<::iovec, 3> iov{};
iov[0].iov_base = &write_id;
iov[0].iov_len  = sizeof(write_id);

iov[1].iov_base = &payload_header;
iov[1].iov_len  = sizeof(payload_header);

iov[2].iov_base = const_cast<char*>(url.data());
iov[2].iov_len  = url.size() + 1;

ssize_t bytes_written = ::writev(fd, iov.data(), iov.size());
