size_t mem_align = stx.stx_dio_mem_align;
const size_t buffer_bytes = 65536; // 64 КБ

if ((stx.stx_mask & STATX_DIOALIGN) == 0 || mem_align == 0) {
    mem_align = static_cast<size_t>(::sysconf(_SC_PAGESIZE));
}

// У C++17/C++20 використовується std::aligned_alloc або posix_memalign
void* raw_ptr = nullptr;
if (::posix_memalign(&raw_ptr, mem_align, buffer_bytes) != 0) {
    throw std::bad_alloc();
}
std::unique_ptr<char, decltype(&::free)> buffer(static_cast<char*>(raw_ptr), &::free);

ssize_t bytes_read = ::pread(fd, buffer.get(), buffer_bytes, aligned_offset);
