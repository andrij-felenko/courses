// luks2dump — читає обидві копії метаданих LUKS2, обирає чинну за seqid
// і проганяє документ JSON через перевірки §11.
//
// Збірка (потрібні OpenSSL і заголовковий nlohmann/json):
//   c++ -std=c++23 -Wall -Wextra -O2 -o luks2dump src/*.cpp -lcrypto
// Запуск (треба право читати сирий пристрій):
//   sudo ./luks2dump /dev/nvme0n1p3
//   ./luks2dump luks2_header_backup.img
#include "header.hpp"
#include "metadata.hpp"

#include <format>
#include <iostream>
#include <string_view>

namespace {

void show(std::string_view name, const luks2::Header& header) {
    std::cout << std::format("{}: seqid={} hdr_size={} ({} КіБ) csum_alg={}\n", name,
                             header.seqid(), header.hdr_size(),
                             header.hdr_size() / 1024, header.csum_alg());
    std::cout << std::format("    uuid={} label=\"{}\" subsystem=\"{}\"\n",
                             header.uuid(), header.label(), header.subsystem());
    std::cout << std::format("    json: {} із {} байтів, хвіст занулено\n",
                             header.json().size(), header.json_capacity());
}

// Коли первинна копія читається, вторинна лежить рівно за hdr_size.
// Коли ні — доводиться перебирати стандартні зсуви.
std::expected<luks2::Header, luks2::Error> read_secondary(
    const luks2::Device& device, const luks2::Header* primary) {
    if (primary != nullptr) {
        return luks2::Header::read(device, primary->hdr_size());
    }
    luks2::Error last = luks2::Error::magic;
    for (const auto offset : luks2::kHeaderOffsets) {
        auto header = luks2::Header::read(device, offset);
        if (header) {
            return header;
        }
        last = header.error();
    }
    return std::unexpected(last);
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << std::format("вжиток: {} <пристрій|образ заголовка>\n", argv[0]);
        return 2;
    }

    auto device = luks2::Device::open(argv[1]);
    if (!device) {
        std::cerr << std::format("{}: {}\n", argv[1], luks2::describe(device.error()));
        return 1;
    }

    auto primary = luks2::Header::read(*device, 0);
    auto secondary = read_secondary(*device, primary ? &*primary : nullptr);

    if (primary) {
        show("первинний (зсув 0)", *primary);
    } else {
        std::cout << std::format("первинний (зсув 0): {}\n",
                                 luks2::describe(primary.error()));
    }
    if (secondary) {
        show(std::format("вторинний (зсув {})", secondary->at_offset()), *secondary);
    } else {
        std::cout << std::format("вторинний: {}\n", luks2::describe(secondary.error()));
    }

    // Арбітраж: перемагає валідна копія з більшим seqid.
    const luks2::Header* chosen = nullptr;
    if (primary && secondary) {
        chosen = (secondary->seqid() > primary->seqid()) ? &*secondary : &*primary;
        if (primary->seqid() != secondary->seqid()) {
            std::cout << std::format(
                "\nseqid копій розбігся ({} проти {}) — том просить cryptsetup repair\n",
                primary->seqid(), secondary->seqid());
        }
        if (primary->uuid() != secondary->uuid()) {
            std::cout << "UUID копій різні — у вікні заголовка лежать два різні томи\n";
        }
    } else if (primary) {
        chosen = &*primary;
        std::cout << "\nпрацюємо на первинній копії: вторинна непридатна\n";
    } else if (secondary) {
        chosen = &*secondary;
        std::cout << "\nпрацюємо на вторинній копії: первинну доведеться відновлювати\n";
    } else {
        std::cerr << "\nжодна копія метаданих не читається\n";
        return 1;
    }

    std::cout << std::format("\nчинна копія: зсув {}, seqid {}\n", chosen->at_offset(),
                             chosen->seqid());

    auto metadata = luks2::Metadata::parse(chosen->json());
    if (!metadata) {
        std::cerr << std::format("метадані непридатні: {}\n",
                                 luks2::describe(metadata.error()));
        return 3;
    }

    metadata->print(std::cout);

    const auto findings = metadata->validate(chosen->hdr_size());
    std::cout << "\nперевірка інваріантів:\n";
    if (findings.empty()) {
        std::cout << "  усі інваріанти виконано\n";
    }
    int errors = 0;
    for (const auto& finding : findings) {
        std::cout << std::format("  {} {}\n", finding.is_error() ? "✖" : "⚠",
                                 finding.text);
        errors += finding.is_error() ? 1 : 0;
    }
    std::cout << std::format("\nпідсумок: помилок {}, попереджень {}\n", errors,
                             static_cast<int>(findings.size()) - errors);
    return errors ? 3 : 0;
}
