#include <unistd.h>
#include <sys/types.h>
#include <cstddef>

// У C++ системний виклик доступний у глобальному просторі імен або через ::copy_file_range
extern "C" {
    ssize_t copy_file_range(int fd_in, loff_t *off_in,
                            int fd_out, loff_t *off_out,
                            size_t len, unsigned int flags);
}
