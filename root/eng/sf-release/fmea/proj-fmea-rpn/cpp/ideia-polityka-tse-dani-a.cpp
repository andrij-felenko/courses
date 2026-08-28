#include <array>
#include <cstddef>
#include <map>
#include <optional>
#include <string>
#include <tuple>
#include <vector>
#include <algorithm>
#include <stdexcept>
#include <iostream>
#include <iomanip>

enum class AP {       // Пріоритет дій: три класи, і жодних градацій більше.
    Low = 1,          // ризик прийнятний; записати обґрунтування
    Medium = 2,       // розглянути й задокументувати рішення
    High = 3,         // діяти обов'язково
};

const char* name(AP ap) {
    switch (ap) {
        case AP::Low:    return "LOW";
        case AP::Medium: return "MEDIUM";
        case AP::High:   return "HIGH";
    }
    return "?";
}
