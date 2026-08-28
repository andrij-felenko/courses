#include <cstdint>
#include <cstddef>
#include <array>

struct alignas(4) SeggerRttBuffer {
    const char*  sName{nullptr};
    char*        pBuffer{nullptr};
    unsigned int sizeOfBuffer{0};
    unsigned int wrOff{0};
    unsigned int rdOff{0};
    unsigned int flags{0};
};

struct alignas(4) SeggerRttControlBlock {
    char acID[16]{"SEGGER RTT"};
    int maxNumUpBuffers{3};
    int maxNumDownBuffers{3};
    std::array<SeggerRttBuffer, 3> aUp{};
    std::array<SeggerRttBuffer, 3> aDown{};
};
