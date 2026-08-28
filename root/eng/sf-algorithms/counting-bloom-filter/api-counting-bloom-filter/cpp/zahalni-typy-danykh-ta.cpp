#include <cstdint>
#include <cstddef>
#include <span>
#include <string_view>
#include <vector>
#include <expected>
#include <array>
#include <functional>
#include <filesystem>

namespace algorithms::data_structures {

enum class CbfError {
    InvalidParameter,
    OutOfMemory,
    ElementNotFound,
    BufferTooSmall,
    CorruptedData,
    IncompatibleParameters,
    IoError
};

enum class InsertResult {
    Inserted,
    InsertedWithSaturation
};

using CustomHashFn = std::function<std::pair<uint32_t, uint32_t>(std::string_view, uint32_t)>;

} // namespace algorithms::data_structures
