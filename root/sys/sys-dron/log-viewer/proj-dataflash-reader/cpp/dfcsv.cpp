// dfcsv.cpp — витягти один ряд «ПОВІДОМЛЕННЯ.Поле» з бортового логу ArduPilot у CSV.
// Збірка: c++ -std=c++17 -O2 -o dfcsv dfcsv.cpp
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <map>
#include <string>
#include <vector>

namespace {

constexpr uint8_t HEAD1    = 0xA3;
constexpr uint8_t HEAD2    = 0x95;
constexpr uint8_t FMT_TYPE = 128;   // номер FMT закріплено форматом назавжди
constexpr size_t  HDR      = 3;     // 0xA3, 0x95 і байт типу

// Що каже одна літера рядка формату: скільки байтів, як тлумачити, на що множити.
struct Letter {
    uint8_t size;   // байтів у пакеті
    char    kind;   // 'i' ціле зі знаком, 'u' без знаку, 'f' дробове,
                    // 's' рядок, 'x' масив — не одне число
    double  mult;   // множник, зашитий у саму літеру
};

bool letterInfo(char c, Letter &out) {
    switch (c) {
    case 'b': out = {  1, 'i', 1.0  }; return true;
    case 'B': out = {  1, 'u', 1.0  }; return true;
    case 'M': out = {  1, 'u', 1.0  }; return true;   // номер режиму польоту
    case 'h': out = {  2, 'i', 1.0  }; return true;
    case 'H': out = {  2, 'u', 1.0  }; return true;
    case 'c': out = {  2, 'i', 0.01 }; return true;
    case 'C': out = {  2, 'u', 0.01 }; return true;
    case 'i': out = {  4, 'i', 1.0  }; return true;
    case 'I': out = {  4, 'u', 1.0  }; return true;
    case 'e': out = {  4, 'i', 0.01 }; return true;
    case 'E': out = {  4, 'u', 0.01 }; return true;
    case 'L': out = {  4, 'i', 1e-7 }; return true;   // широта або довгота
    case 'f': out = {  4, 'f', 1.0  }; return true;
    case 'd': out = {  8, 'f', 1.0  }; return true;
    case 'q': out = {  8, 'i', 1.0  }; return true;
    case 'Q': out = {  8, 'u', 1.0  }; return true;
    case 'n': out = {  4, 's', 1.0  }; return true;
    case 'N': out = { 16, 's', 1.0  }; return true;
    case 'Z': out = { 64, 's', 1.0  }; return true;
    case 'a': out = { 64, 'x', 1.0  }; return true;   // int16_t[32]
    default:  return false;
    }
}

struct Field  { std::string label; size_t off; char code; Letter type; };
struct Layout { std::string name; uint8_t length = 0; std::vector<Field> fields; };
