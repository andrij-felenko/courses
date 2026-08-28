#include <cstdio>
#include <iostream>
#include <memory>
#include <vector>

// У C++ керування буферизацією потоків stdio здійснюється через std::setvbuf,
// а для потоків iostream — через синхронізацію та прив'язку потоків.
void configure_stream_buffering(std::FILE* stream, int mode, std::size_t size) {
    if (std::setvbuf(stream, nullptr, mode, size) != 0) {
        std::perror("setvbuf failed");
    }
}
