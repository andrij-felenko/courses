#include "metadata.hpp"

#include <algorithm>
#include <charconv>
#include <format>
#include <optional>
#include <ostream>

namespace luks2 {
namespace {

using nlohmann::json;

const json* find(const json& object, std::string_view key) {
    if (!object.is_object()) {
        return nullptr;
    }
    const auto it = object.find(std::string{key});
    return it == object.end() ? nullptr : &*it;
}

std::optional<std::string> string_field(const json& object, std::string_view key) {
    const json* value = find(object, key);
    if (value == nullptr || !value->is_string()) {
        return std::nullopt;
    }
    return value->get<std::string>();
}

std::optional<std::int64_t> int_field(const json& object, std::string_view key) {
    const json* value = find(object, key);
    if (value == nullptr || !value->is_number_integer()) {
        return std::nullopt;
    }
    return value->get<std::int64_t>();
}

const json* object_field(const json& object, std::string_view key) {
    const json* value = find(object, key);
    return (value != nullptr && value->is_object()) ? value : nullptr;
}

const json* array_field(const json& object, std::string_view key) {
    const json* value = find(object, key);
    return (value != nullptr && value->is_array()) ? value : nullptr;
}

// Зсуви й розміри LUKS2 тримає рядками: 64 біти не влазять у число JSON.
std::optional<std::uint64_t> decimal_field(const json& object, std::string_view key) {
    const auto text = string_field(object, key);
    if (!text || text->empty()) {
        return std::nullopt;
    }
    std::uint64_t value = 0;
    const char* first = text->data();
    const char* last = first + text->size();
    const auto [ptr, ec] = std::from_chars(first, last, value);
    if (ec != std::errc{} || ptr != last) {
        return std::nullopt;
    }
    return value;
}

bool contains(std::span<const std::string_view> list, std::string_view value) {
    return std::ranges::find(list, value) != list.end();
}

struct Area {
    std::uint64_t offset;
    std::uint64_t size;
    std::string slot;
};

class Checker {
public:
    Checker(const json& document, std::uint64_t hdr_size)
        : document_{document}, hdr_size_{hdr_size} {}

    std::vector<Finding> run();

private:
    template <typename... Args>
    void error(std::format_string<Args...> fmt, Args&&... args) {
        findings_.push_back({Finding::Level::error,
                             std::format(fmt, std::forward<Args>(args)...)});
    }
    template <typename... Args>
    void warn(std::format_string<Args...> fmt, Args&&... args) {
        findings_.push_back({Finding::Level::warning,
                             std::format(fmt, std::forward<Args>(args)...)});
    }

    void check_config(const json& config);
    void check_keyslot(const std::string& id, const json& slot, const json& keyslots);
    void check_kdf(const std::string& id, const json& slot);
    void add_area(const std::string& id, std::uint64_t offset, std::uint64_t size);
    void check_segment(const std::string& id, const json& segment);
    void check_digest(const std::string& id, const json& digest,
                      const json& keyslots, const json& segments);
    void check_refs(const json& owner, std::string_view owner_dict,
                    const std::string& owner_id, std::string_view array_name,
                    const json& target, std::string_view target_name);
    void check_unbound(const json& keyslots, const json& digests, const json& config);

    const json& document_;
    std::uint64_t hdr_size_;
    std::uint64_t keyslots_size_{0};
    std::vector<Area> areas_;
    std::vector<Finding> findings_;
};

void Checker::check_refs(const json& owner, std::string_view owner_dict,
                         const std::string& owner_id, std::string_view array_name,
                         const json& target, std::string_view target_name) {
    const json* refs = array_field(owner, array_name);
    if (refs == nullptr) {
        error("{}[\"{}\"]: немає обов'язкового масиву {}", owner_dict, owner_id, array_name);
        return;
    }
    if (refs->empty()) {
        warn("{}[\"{}\"].{} порожній", owner_dict, owner_id, array_name);
    }
    for (const auto& ref : *refs) {
        if (!ref.is_string()) {
            error("{}[\"{}\"].{}: посилання мусить бути рядком",
                  owner_dict, owner_id, array_name);
            continue;
        }
        const auto id = ref.get<std::string>();
        if (!target.contains(id)) {
            error("{}[\"{}\"].{}: висяче посилання на {}[\"{}\"]",
                  owner_dict, owner_id, array_name, target_name, id);
        }
    }
}

void Checker::check_config(const json& config) {
    static constexpr std::array<std::string_view, 6> known_flags{
        "allow-discards", "same-cpu-crypt", "submit-from-crypt-cpus",
        "no-read-workqueue", "no-write-workqueue", "no-journal"};
    static constexpr std::array<std::string_view, 9> known_requirements{
        "online-reencrypt", "online-reencrypt-v2", "online-reencrypt-v3",
        "offline-reencrypt", "direct-key", "integrity", "unbound-keyslots",
        "opal", "opal-hw-only"};

    if (const auto json_size = decimal_field(config, "json_size")) {
        if (*json_size != hdr_size_ - kHdrTotalSize) {
            error("config.json_size={}, а зона тримає {}", *json_size,
                  hdr_size_ - kHdrTotalSize);
        }
    } else {
        error("config.json_size: немає або не десятковий рядок");
    }

    if (const auto keyslots_size = decimal_field(config, "keyslots_size")) {
        keyslots_size_ = *keyslots_size;
        if (keyslots_size_ % 4096 != 0) {
            error("config.keyslots_size={} не кратний 4096", keyslots_size_);
        }
    } else {
        error("config.keyslots_size: немає або не десятковий рядок");
    }

    if (const json* flags = array_field(config, "flags")) {
        for (const auto& flag : *flags) {
            if (!flag.is_string()) {
                error("config.flags: елемент не рядок");
            } else if (!contains(known_flags, flag.get<std::string>())) {
                warn("config.flags: невідомий прапорець \"{}\"", flag.get<std::string>());
            }
        }
    }

    if (const json* reqs = array_field(config, "requirements")) {
        for (const auto& req : *reqs) {
            if (!req.is_string()) {
                error("config.requirements: елемент не рядок");
            } else if (!contains(known_requirements, req.get<std::string>())) {
                // саме тут libcryptsetup віддає -EINVAL і не чіпає том
                error("config.requirements: невідома вимога \"{}\" — том буде заблоковано",
                      req.get<std::string>());
            }
        }
    }
}

void Checker::add_area(const std::string& id, std::uint64_t offset, std::uint64_t size) {
    const std::uint64_t metadata_end = 2 * hdr_size_;

    if (offset % 4096 != 0) {
        error("keyslots[\"{}\"].area.offset={} не вирівняно на 4096", id, offset);
    }
    if (offset < metadata_end) {
        error("keyslots[\"{}\"].area починається в зоні заголовків [0..{})",
              id, metadata_end);
    }
    for (const auto& area : areas_) {
        if (offset < area.offset + area.size && area.offset < offset + size) {
            error("області шпарин \"{}\" і \"{}\" перекриваються", id, area.slot);
        }
    }
    areas_.push_back({offset, size, id});
}

void Checker::check_kdf(const std::string& id, const json& slot) {
    const json* kdf = object_field(slot, "kdf");
    if (kdf == nullptr) {
        error("keyslots[\"{}\"]: немає об'єкта kdf", id);
        return;
    }
    const auto type = string_field(*kdf, "type");
    if (!type) {
        error("keyslots[\"{}\"].kdf: немає поля type", id);
        return;
    }
    const auto salt = string_field(*kdf, "salt");
    if (!salt || salt->size() < 22) {  // 16 байтів у base64 — 24 символи
        error("keyslots[\"{}\"].kdf.salt: сіль коротша за 16 байтів", id);
    }

    if (*type == "argon2id" || *type == "argon2i") {
        if (int_field(*kdf, "time").value_or(0) < 1) {
            error("keyslots[\"{}\"].kdf.time: немає або менше за 1", id);
        }
        const auto memory = int_field(*kdf, "memory").value_or(0);
        if (memory < 32) {
            error("keyslots[\"{}\"].kdf.memory: немає або нижче мінімуму Argon2", id);
        } else if (memory < 65536) {
            warn("keyslots[\"{}\"].kdf.memory={} КіБ — це слабше за типовий 1 ГіБ", id, memory);
        }
        if (int_field(*kdf, "cpus").value_or(0) < 1) {
            error("keyslots[\"{}\"].kdf.cpus: немає або менше за 1", id);
        }
    } else if (*type == "pbkdf2") {
        if (int_field(*kdf, "iterations").value_or(0) < 1000) {
            error("keyslots[\"{}\"].kdf.iterations: немає або надто мало", id);
        }
        if (!string_field(*kdf, "hash")) {
            error("keyslots[\"{}\"].kdf.hash: немає геш-функції PBKDF2", id);
        }
    } else {
        error("keyslots[\"{}\"].kdf.type=\"{}\": формат такого KDF не знає", id, *type);
    }
}

void Checker::check_keyslot(const std::string& id, const json& slot,
                            const json& keyslots) {
    static constexpr std::array<std::string_view, 3> modes{
        "reencrypt", "encrypt", "decrypt"};
    static constexpr std::array<std::string_view, 2> directions{"forward", "backward"};
    static constexpr std::array<std::string_view, 6> resiliences{
        "journal", "checksum", "none", "datashift", "datashift-journal",
        "datashift-checksum"};

    const auto type = string_field(slot, "type");
    if (!type) {
        error("keyslots[\"{}\"]: немає поля type", id);
        return;
    }

    if (*type == "reencrypt") {
        const auto mode = string_field(slot, "mode").value_or("");
        if (!contains(modes, mode)) {
            error("keyslots[\"{}\"].mode: немає або невідомий режим міграції", id);
        }
        if (!contains(directions, string_field(slot, "direction").value_or(""))) {
            error("keyslots[\"{}\"].direction: немає або не forward/backward", id);
        }
        if (!contains(resiliences, string_field(slot, "resilience").value_or(""))) {
            error("keyslots[\"{}\"].resilience: немає або невідомий механізм", id);
        }
        if (const auto ref = int_field(slot, "keyslot")) {
            const auto ref_id = std::format("{}", *ref);
            if (!keyslots.contains(ref_id)) {
                error("keyslots[\"{}\"].keyslot={}: такої шпарини немає", id, ref_id);
            }
        } else {
            error("keyslots[\"{}\"].keyslot: немає посилання на слот нового ключа", id);
        }
        return;
    }

    if (*type != "luks2") {
        warn("keyslots[\"{}\"].type=\"{}\": невідомий тип шпарини", id, *type);
        return;
    }

    const auto key_size = int_field(slot, "key_size").value_or(0);
    if (key_size <= 0) {
        error("keyslots[\"{}\"].key_size: немає або не додатне", id);
    }
    if (const auto priority = int_field(slot, "priority")) {
        if (*priority < 0 || *priority > 2) {
            warn("keyslots[\"{}\"].priority={} поза 0..2", id, *priority);
        }
    } else {
        error("keyslots[\"{}\"].priority: немає поля", id);
    }

    std::int64_t stripes = 0;
    if (const json* af = object_field(slot, "af")) {
        if (string_field(*af, "type").value_or("") != "luks1") {
            error("keyslots[\"{}\"].af.type: стандарт знає лише \"luks1\"", id);
        }
        stripes = int_field(*af, "stripes").value_or(0);
        if (stripes <= 0) {
            error("keyslots[\"{}\"].af.stripes: немає або не додатне", id);
        }
        if (!string_field(*af, "hash")) {
            error("keyslots[\"{}\"].af.hash: немає геш-функції дифузії", id);
        }
    } else {
        error("keyslots[\"{}\"]: немає об'єкта af", id);
    }

    if (const json* area = object_field(slot, "area")) {
        if (string_field(*area, "type").value_or("") != "raw") {
            error("keyslots[\"{}\"].area.type: очікується \"raw\"", id);
        }
        if (!string_field(*area, "encryption")) {
            error("keyslots[\"{}\"].area.encryption: немає специфікації шифру", id);
        }
        if (int_field(*area, "key_size").value_or(0) <= 0) {
            error("keyslots[\"{}\"].area.key_size: немає або не додатне", id);
        }
        const auto offset = decimal_field(*area, "offset");
        const auto size = decimal_field(*area, "size");
        if (!offset || !size) {
            error("keyslots[\"{}\"].area: offset/size мусять бути десятковими рядками", id);
        } else {
            const auto needed =
                static_cast<std::uint64_t>(std::max<std::int64_t>(stripes, 0)) *
                static_cast<std::uint64_t>(std::max<std::int64_t>(key_size, 0));
            if (needed > 0 && *size < needed) {
                error("keyslots[\"{}\"].area.size={} менше за stripes·key_size={}",
                      id, *size, needed);
            }
            add_area(id, *offset, *size);
        }
    } else {
        error("keyslots[\"{}\"]: немає об'єкта area", id);
    }

    check_kdf(id, slot);
}

void Checker::check_segment(const std::string& id, const json& segment) {
    static constexpr std::array<std::int64_t, 4> sector_sizes{512, 1024, 2048, 4096};

    const auto type = string_field(segment, "type");
    if (!type) {
        error("segments[\"{}\"]: немає поля type", id);
        return;
    }
    if (*type != "crypt" && *type != "linear") {
        warn("segments[\"{}\"].type=\"{}\": невідомий тип сегмента", id, *type);
        return;
    }

    const auto offset = decimal_field(segment, "offset");
    if (!offset) {
        error("segments[\"{}\"].offset: немає або не десятковий рядок", id);
        return;
    }

    const auto size_text = string_field(segment, "size");
    std::optional<std::uint64_t> size;
    bool dynamic = false;
    if (!size_text) {
        error("segments[\"{}\"].size: немає поля", id);
    } else if (*size_text == "dynamic") {
        dynamic = true;
    } else {
        size = decimal_field(segment, "size");
        if (!size) {
            error("segments[\"{}\"].size: ні \"dynamic\", ні десятковий рядок", id);
        }
    }

    const std::uint64_t metadata_end = 2 * hdr_size_;
    if (*offset < metadata_end) {
        error("segments[\"{}\"].offset={} заходить у зону заголовків", id, *offset);
    } else if (*offset < metadata_end + keyslots_size_) {
        warn("segments[\"{}\"].offset={} менший за межу зони шпарин {}",
             id, *offset, metadata_end + keyslots_size_);
    }
    for (const auto& area : areas_) {
        const bool overlaps = *offset < area.offset + area.size &&
                              (dynamic || !size || area.offset < *offset + *size);
        if (overlaps) {
            error("segments[\"{}\"] перекриває область шпарини \"{}\"", id, area.slot);
        }
    }

    if (*type == "linear") {
        return;
    }

    if (!decimal_field(segment, "iv_tweak")) {
        error("segments[\"{}\"].iv_tweak: немає або не десятковий рядок", id);
    }
    if (!string_field(segment, "encryption")) {
        error("segments[\"{}\"].encryption: немає специфікації шифру ядра", id);
    }
    if (const auto sector = int_field(segment, "sector_size")) {
        if (!std::ranges::contains(sector_sizes, *sector)) {
            error("segments[\"{}\"].sector_size={}: дозволені 512/1024/2048/4096",
                  id, *sector);
        }
    } else {
        error("segments[\"{}\"].sector_size: немає поля", id);
    }

    if (const json* integrity = object_field(segment, "integrity")) {
        if (!string_field(*integrity, "type")) {
            error("segments[\"{}\"].integrity.type: немає типу автентифікації", id);
        }
        if (!int_field(*integrity, "sector_size")) {
            warn("segments[\"{}\"].integrity.sector_size: немає, ядро візьме 512", id);
        }
    }
}

void Checker::check_digest(const std::string& id, const json& digest,
                           const json& keyslots, const json& segments) {
    const auto type = string_field(digest, "type");
    if (!type) {
        error("digests[\"{}\"]: немає поля type", id);
        return;
    }
    if (!string_field(digest, "salt")) {
        error("digests[\"{}\"].salt: немає солі", id);
    }
    if (!string_field(digest, "digest")) {
        error("digests[\"{}\"].digest: немає контрольного дайджесту", id);
    }
    if (!string_field(digest, "hash")) {
        error("digests[\"{}\"].hash: немає геш-функції", id);
    }
    if (*type == "pbkdf2") {
        if (int_field(digest, "iterations").value_or(0) < 1000) {
            error("digests[\"{}\"].iterations: немає або надто мало", id);
        }
    } else if (type->starts_with("argon2")) {
        if (!int_field(digest, "time") || !int_field(digest, "memory") ||
            !int_field(digest, "cpus")) {
            error("digests[\"{}\"]: для Argon2 потрібні time/memory/cpus", id);
        }
    } else {
        warn("digests[\"{}\"].type=\"{}\": невідомий алгоритм верифікації", id, *type);
    }

    check_refs(digest, "digests", id, "keyslots", keyslots, "keyslots");
    check_refs(digest, "digests", id, "segments", segments, "segments");
}

void Checker::check_unbound(const json& keyslots, const json& digests,
                            const json& config) {
    bool allowed = false;
    if (const json* reqs = array_field(config, "requirements")) {
        allowed = std::ranges::any_of(*reqs, [](const json& r) {
            return r.is_string() && r.get<std::string>() == "unbound-keyslots";
        });
    }
    if (allowed) {
        return;
    }

    for (const auto& [id, slot] : keyslots.items()) {
        if (string_field(slot, "type").value_or("") == "reencrypt") {
            continue;
        }
        const bool bound = std::ranges::any_of(digests, [&](const json& digest) {
            const json* refs = array_field(digest, "keyslots");
            return refs != nullptr && std::ranges::any_of(*refs, [&](const json& r) {
                return r.is_string() && r.get<std::string>() == id;
            });
        });
        if (!bound) {
            warn("keyslots[\"{}\"] не прив'язана до жодного дайджесту", id);
        }
    }
}

std::vector<Finding> Checker::run() {
    const json* keyslots = object_field(document_, "keyslots");
    const json* tokens = object_field(document_, "tokens");
    const json* segments = object_field(document_, "segments");
    const json* digests = object_field(document_, "digests");
    const json* config = object_field(document_, "config");

    if (!keyslots || !tokens || !segments || !digests || !config) {
        error("корінь мусить мати словники keyslots, tokens, segments, digests, config");
        return std::move(findings_);
    }

    check_config(*config);
    for (const auto& [id, slot] : keyslots->items()) {
        check_keyslot(id, slot, *keyslots);
    }
    for (const auto& [id, segment] : segments->items()) {
        check_segment(id, segment);
    }
    for (const auto& [id, digest] : digests->items()) {
        check_digest(id, digest, *keyslots, *segments);
    }
    for (const auto& [id, token] : tokens->items()) {
        if (!string_field(token, "type")) {
            error("tokens[\"{}\"]: немає поля type", id);
        }
        check_refs(token, "tokens", id, "keyslots", *keyslots, "keyslots");
    }
    check_unbound(*keyslots, *digests, *config);

    return std::move(findings_);
}

}  // namespace

std::expected<Metadata, Error> Metadata::parse(std::string_view text) {
    auto document = json::parse(text, nullptr, /*allow_exceptions=*/false);
    if (document.is_discarded()) {
        return std::unexpected(Error::json_syntax);
    }
    if (!document.is_object()) {
        return std::unexpected(Error::json_schema);
    }
    return Metadata{std::move(document)};
}

void Metadata::print(std::ostream& out) const {
    out << "\nграф метаданих:\n";

    if (const json* keyslots = object_field(document_, "keyslots")) {
        for (const auto& [id, slot] : keyslots->items()) {
            const json* area = object_field(slot, "area");
            const json* kdf = object_field(slot, "kdf");
            out << std::format(
                "  keyslot {:<3} type={:<9} kdf={:<9} area={}+{}\n", id,
                string_field(slot, "type").value_or("?"),
                kdf ? string_field(*kdf, "type").value_or("?") : "-",
                area ? string_field(*area, "offset").value_or("?") : "-",
                area ? string_field(*area, "size").value_or("?") : "-");
        }
    }
    if (const json* tokens = object_field(document_, "tokens")) {
        for (const auto& [id, token] : tokens->items()) {
            out << std::format("  token   {:<3} type={}\n", id,
                               string_field(token, "type").value_or("?"));
        }
    }
    if (const json* segments = object_field(document_, "segments")) {
        for (const auto& [id, segment] : segments->items()) {
            out << std::format(
                "  segment {:<3} type={:<7} offset={} size={} enc={} sector={}\n", id,
                string_field(segment, "type").value_or("?"),
                string_field(segment, "offset").value_or("?"),
                string_field(segment, "size").value_or("?"),
                string_field(segment, "encryption").value_or("-"),
                int_field(segment, "sector_size").value_or(0));
        }
    }
    if (const json* digests = object_field(document_, "digests")) {
        for (const auto& [id, digest] : digests->items()) {
            out << std::format("  digest  {:<3} type={}\n", id,
                               string_field(digest, "type").value_or("?"));
        }
    }
}

std::vector<Finding> Metadata::validate(std::uint64_t hdr_size) const {
    return Checker{document_, hdr_size}.run();
}

}  // namespace luks2
