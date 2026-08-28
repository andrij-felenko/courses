// C++ Implementation: Modern RAII ACPI Table Inspector & AML Parser (C++20)
#include <iostream>
#include <fstream>
#include <vector>
#include <array>
#include <string_view>
#include <span>
#include <numeric>
#include <cstdint>
#include <memory>

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

class AcpiTableParser {
public:
    static bool validateChecksum(std::span<const std::uint8_t> data) noexcept {
        if (data.empty()) return false;
        const std::uint8_t sum = std::accumulate(
            data.begin(), data.end(), static_cast<std::uint8_t>(0)
        );
        return sum == 0;
    }

    static std::pair<std::size_t, std::size_t> parseAmlPkgLength(std::span<const std::uint8_t> amlData) noexcept {
        if (amlData.empty()) return {0, 0};
        const std::uint8_t lead = amlData[0];
        const std::uint8_t byteCount = (lead >> 6) & 0x03;

        if (byteCount == 0) {
            return {static_cast<std::size_t>(lead & 0x3F), 1};
        }

        if (amlData.size() < static_cast<std::size_t>(byteCount + 1)) {
            return {0, 0};
        }

        std::size_t length = (lead & 0x0F);
        for (std::uint8_t i = 0; i < byteCount; ++i) {
            length |= (static_cast<std::size_t>(amlData[1 + i]) << (4 + i * 8));
        }
        return {length, static_cast<std::size_t>(byteCount + 1)};
    }

    static bool inspectTable(std::string_view path) {
        std::ifstream file(path.data(), std::ios::binary | std::ios::ate);
        if (!file.is_open()) {
            std::cerr << "Error: Cannot open ACPI table file: " << path << '\n';
            return false;
        }

        const auto fileSize = static_cast<std::size_t>(file.tellg());
        file.seekg(0, std::ios::beg);

        if (fileSize < sizeof(AcpiTableHeader)) {
            std::cerr << "Error: File size (" << fileSize << " bytes) is smaller than ACPI header\n";
            return false;
        }

        std::vector<std::uint8_t> buffer(fileSize);
        if (!file.read(reinterpret_cast<char*>(buffer.data()), fileSize)) {
            std::cerr << "Error: Failed to read binary table data\n";
            return false;
        }

        const auto* hdr = reinterpret_cast<const AcpiTableHeader*>(buffer.data());
        const std::string_view sig(hdr->signature.data(), 4);
        const std::string_view oem(hdr->oem_id.data(), 6);
        const std::string_view oemTable(hdr->oem_table_id.data(), 8);
        const std::string_view compiler(hdr->asl_compiler_id.data(), 4);

        const bool isChecksumValid = validateChecksum(buffer);

        std::cout << "========================================\n";
        std::cout << "   Modern C++20 ACPI Table Inspector    \n";
        std::cout << "========================================\n";
        std::cout << "Signature:         " << sig << '\n';
        std::cout << "Header Length:     " << hdr->length << " bytes\n";
        std::cout << "File Raw Size:     " << fileSize << " bytes\n";
        std::cout << "Revision:          " << static_cast<int>(hdr->revision) << '\n';
        std::cout << "OEM ID:            " << oem << '\n';
        std::cout << "OEM Table ID:      " << oemTable << '\n';
        std::cout << "ASL Compiler:      " << compiler << '\n';
        std::cout << "Checksum Status:   " << (isChecksumValid ? "VALID (0x00)" : "INVALID") << '\n';

        if (sig == "DSDT" || sig == "SSDT") {
            const std::span<const std::uint8_t> fullSpan(buffer);
            if (fullSpan.size() > sizeof(AcpiTableHeader)) {
                const auto amlPayload = fullSpan.subspan(sizeof(AcpiTableHeader));
                std::cout << "AML Bytecode Size: " << amlPayload.size() << " bytes\n";

                const auto [pkgLen, bytesRead] = parseAmlPkgLength(amlPayload);
                std::cout << "Root AML PkgLength: " << pkgLen << " bytes (header bytes: " << bytesRead << ")\n";
            }
        }

        return isChecksumValid;
    }
};

int main(int argc, char** argv) {
    const std::string_view path = (argc > 1) ? argv[1] : "/sys/firmware/acpi/tables/FADT";
    return AcpiTableParser::inspectTable(path) ? 0 : 1;
}
