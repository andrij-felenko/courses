// C++ Implementation: RAII ACPI Sysfs Inspector using C++20
#include <iostream>
#include <fstream>
#include <vector>
#include <array>
#include <string_view>
#include <numeric>
#include <cstdint>
#include <expected>

#pragma pack(push, 1)
struct alignas(1) AcpiTableHeader {
    std::array<char, 4> signature;
    std::uint32_t       length;
    std::uint8_t        revision;
    std::uint8_t        checksum;
    std::array<char, 6> oem_id;
    std::array<char, 8> oem_table_id;
    std::uint32_t       oem_revision;
    std::array<char, 4> asl_compiler_id;
    std::uint32_t       asl_compiler_revision;
};
#pragma pack(pop)

enum class AcpiParseError {
    FileNotFound,
    HeaderTruncated,
    ReadFailure,
    ChecksumMismatch
};

class AcpiSysfsParser {
public:
    static std::expected<AcpiTableHeader, AcpiParseError>
    inspectTable(std::string_view sysfsPath) {
        std::ifstream file(sysfsPath.data(), std::ios::binary | std::ios::ate);
        if (!file.is_open()) {
            return std::unexpected(AcpiParseError::FileNotFound);
        }

        const auto fileSize = static_cast<std::size_t>(file.tellg());
        file.seekg(0, std::ios::beg);

        if (fileSize < sizeof(AcpiTableHeader)) {
            return std::unexpected(AcpiParseError::HeaderTruncated);
        }

        std::vector<std::uint8_t> buffer(fileSize);
        if (!file.read(reinterpret_cast<char*>(buffer.data()), fileSize)) {
            return std::unexpected(AcpiParseError::ReadFailure);
        }

        const auto sum = std::accumulate(buffer.begin(), buffer.end(), static_cast<std::uint8_t>(0));
        if (sum != 0) {
            return std::unexpected(AcpiParseError::ChecksumMismatch);
        }

        AcpiTableHeader header{};
        std::copy_n(buffer.data(), sizeof(AcpiTableHeader), reinterpret_cast<std::uint8_t*>(&header));
        return header;
    }
};

int main() {
    constexpr std::string_view path = "/sys/firmware/acpi/tables/FADT";
    auto result = AcpiSysfsParser::inspectTable(path);

    if (result) {
        const auto& hdr = *result;
        std::cout << "Signature:  " << std::string_view(hdr.signature.data(), 4) << '\n';
        std::cout << "Table Size: " << hdr.length << " bytes\n";
        std::cout << "OEM ID:     " << std::string_view(hdr.oem_id.data(), 6) << '\n';
        std::cout << "Status:     Checksum verified successfully.\n";
    } else {
        std::cerr << "Failed to parse ACPI table from sysfs.\n";
    }
    return 0;
}
