// cpio_newc_header.hpp — Ідіоматична специфікація заголовка мовою C++20
#include <array>
#include <cstdint>
#include <string_view>

namespace cpio {

struct alignas(1) Header {
    std::array<char, 6>  magic;     // "070701" або "070702"
    std::array<char, 8>  ino;       // Hex ASCII номер іноди
    std::array<char, 8>  mode;      // Hex ASCII тип і права доступу
    std::array<char, 8>  uid;       // Hex ASCII User ID
    std::array<char, 8>  gid;       // Hex ASCII Group ID
    std::array<char, 8>  nlink;     // Hex ASCII лічильник посилань
    std::array<char, 8>  mtime;     // Hex ASCII час модифікації
    std::array<char, 8>  filesize;  // Hex ASCII розмір даних у байтах
    std::array<char, 8>  maj;       // Hex ASCII Major dev іноди
    std::array<char, 8>  min;       // Hex ASCII Minor dev іноди
    std::array<char, 8>  rmaj;      // Hex ASCII Major dev пристрою
    std::array<char, 8>  rmin;      // Hex ASCII Minor dev пристрою
    std::array<char, 8>  namesize;  // Hex ASCII довжина шляху з '\0'
    std::array<char, 8>  chksum;    // Hex ASCII CRC32 або 0
};

static_assert(sizeof(Header) == 110, "Заголовок CPIO newc мусить бути точно 110 байтів");

} // namespace cpio
