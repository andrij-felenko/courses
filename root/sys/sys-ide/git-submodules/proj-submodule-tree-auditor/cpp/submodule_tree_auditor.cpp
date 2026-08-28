// submodule_tree_auditor.cpp — Повноцінний аудитор підмодулів та ліцензій на C++20
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <filesystem>
#include <expected>
#include <span>
#include <cstdint>
#include <format>
#include <algorithm>
#include <unordered_set>

namespace fs = std::filesystem;

namespace auditor {

constexpr uint32_t DIRC_MAGIC = 0x44495243;
constexpr uint32_t MODE_GITLINK = 0160000;
constexpr int MAX_RECURSION_DEPTH = 16;

enum class AuditStatus {
    Ok = 0,
    Uninitialized = 1,
    CommitDrift = 2,
    InsecureUrl = 3,
    ConfigMismatch = 4
};

enum class LicenseCategory {
    Unknown = 0,
    Permissive = 1,
    WeakCopyleft = 2,
    StrongCopyleft = 3
};

struct SubmoduleNode {
    std::string path;
    std::string url;
    std::string index_sha;
    std::string head_sha;
    std::string detected_license{"UNKNOWN"};
    LicenseCategory license_category{LicenseCategory::Unknown};
    AuditStatus status{AuditStatus::Ok};
    bool in_gitmodules{false};
    bool in_index{false};
    int depth{0};
};

enum class AuditError {
    FileNotFound,
    InvalidMagic,
    UnsupportedVersion,
    CorruptedData,
    RecursionLimitExceeded
};

class SubmoduleTreeAuditor {
public:
    static std::expected<std::vector<SubmoduleNode>, AuditError>
    audit_tree(const fs::path& root_path) {
        std::vector<SubmoduleNode> results;
        std::unordered_set<std::string> visited;

        auto status = audit_recursive(root_path, "", 0, results, visited);
        if (!status) return std::unexpected(status.error());

        return results;
    }

    static void print_report(const std::vector<SubmoduleNode>& nodes) {
        std::cout << "\n================================= RECURSIVE SUBMODULE AUDIT REPORT =================================\n";
        std::cout << std::format("{:<4} {:<28} {:<12} {:<18} {:<12} {}\n",
                                 "LVL", "SUBMODULE PATH", "STATUS", "SPDX LICENSE", "CATEGORY", "COMMIT DIVERGENCE (INDEX -> HEAD)");
        std::cout << "----------------------------------------------------------------------------------------------------\n";

        for (const auto& node : nodes) {
            std::string_view st_str = "OK";
            switch (node.status) {
                case AuditStatus::Uninitialized: st_str = "UNINIT"; break;
                case AuditStatus::CommitDrift: st_str = "DRIFT"; break;
                case AuditStatus::InsecureUrl: st_str = "INSECURE"; break;
                case AuditStatus::ConfigMismatch: st_str = "MISMATCH"; break;
                default: break;
            }

            std::string_view cat_str = "UNKNOWN";
            switch (node.license_category) {
                case LicenseCategory::Permissive: cat_str = "PERMISSIVE"; break;
                case LicenseCategory::WeakCopyleft: cat_str = "WEAK-COPY"; break;
                case LicenseCategory::StrongCopyleft: cat_str = "STRONG-COPY"; break;
                default: break;
            }

            std::string s_idx = node.index_sha.substr(0, std::min<size_t>(8, node.index_sha.size()));
            std::string s_head = node.head_sha.substr(0, std::min<size_t>(8, node.head_sha.size()));

            std::cout << std::format("[{}]  {:<28} {:<12} {:<18} {:<12} {} -> {}\n",
                                     node.depth, node.path, st_str, node.detected_license, cat_str, s_idx, s_head);
        }
        std::cout << "====================================================================================================\n\n";
    }

    static void export_sbom(const fs::path& out_path, const std::vector<SubmoduleNode>& nodes) {
        std::ofstream out(out_path);
        if (!out.is_open()) return;

        out << "{\n";
        out << "  \"$schema\": \"https://cyclonedx.org/schema/bom-1.5.json\",\n";
        out << "  \"bomFormat\": \"CycloneDX\",\n";
        out << "  \"specVersion\": \"1.5\",\n";
        out << "  \"components\": [\n";

        for (size_t i = 0; i < nodes.size(); ++i) {
            const auto& n = nodes[i];
            out << "    {\n";
            out << "      \"type\": \"library\",\n";
            out << std::format("      \"name\": \"{}\",\n", n.path);
            out << std::format("      \"version\": \"{}\",\n", n.index_sha);
            out << std::format("      \"purl\": \"pkg:generic/{}@{}\",\n", n.path, n.index_sha);
            out << "      \"externalReferences\": [\n";
            out << "        {\n";
            out << "          \"type\": \"vcs\",\n";
            out << std::format("          \"url\": \"{}\"\n", n.url);
            out << "        }\n";
            out << "      ],\n";
            out << "      \"licenses\": [\n";
            out << "        {\n";
            out << "          \"license\": {\n";
            out << std::format("            \"id\": \"{}\"\n", n.detected_license);
            out << "          }\n";
            out << "        }\n";
            out << "      ],\n";
            out << "      \"properties\": [\n";
            out << std::format("        {{\"name\": \"audit:status\", \"value\": \"{}\"}},\n", static_cast<int>(n.status));
            out << std::format("        {{\"name\": \"audit:headSha\", \"value\": \"{}\"}},\n", n.head_sha);
            out << std::format("        {{\"name\": \"audit:depth\", \"value\": \"{}\"}}\n", n.depth);
            out << "      ]\n";
            out << "    }" << (i + 1 < nodes.size() ? "," : "") << "\n";
        }
        out << "  ]\n}\n";
    }

private:
    static uint32_t parse_be32(std::span<const uint8_t, 4> b) noexcept {
        return (static_cast<uint32_t>(b[0]) << 24) |
               (static_cast<uint32_t>(b[1]) << 16) |
               (static_cast<uint32_t>(b[2]) << 8)  |
               (static_cast<uint32_t>(b[3]));
    }

    static std::string hex_sha(std::span<const uint8_t, 20> sha) {
        std::string s;
        s.reserve(40);
        for (uint8_t byte : sha) s += std::format("{:02x}", byte);
        return s;
    }

    static std::expected<void, AuditError>
    audit_recursive(const fs::path& repo_root, const std::string& prefix, int depth,
                    std::vector<SubmoduleNode>& nodes, std::unordered_set<std::string>& visited) {
        if (depth > MAX_RECURSION_DEPTH) return std::unexpected(AuditError::RecursionLimitExceeded);

        std::string canonical_root = fs::canonical(repo_root).string();
        if (visited.contains(canonical_root)) return {};
        visited.insert(canonical_root);

        const auto index_path = repo_root / ".git" / "index";
        const auto modules_path = repo_root / ".gitmodules";

        if (fs::exists(index_path)) {
            parse_index(index_path, prefix, depth, nodes);
        }

        if (fs::exists(modules_path)) {
            parse_modules(modules_path, prefix, depth, nodes);
        }

        size_t current_sz = nodes.size();
        for (size_t i = 0; i < current_sz; ++i) {
            auto& node = nodes[i];
            if (node.depth != depth) continue;

            if (node.url.starts_with("http://")) {
                node.status = AuditStatus::InsecureUrl;
            }
            if (!node.in_gitmodules || !node.in_index) {
                node.status = AuditStatus::ConfigMismatch;
            }

            const auto head_file = repo_root / ".git" / "modules" / node.path / "HEAD";
            std::error_code ec;
            if (fs::exists(head_file, ec)) {
                std::ifstream hf(head_file);
                std::string h_line;
                if (std::getline(hf, h_line)) {
                    auto tr_h = trim(h_line);
                    if (tr_h.starts_with("ref: ")) {
                        std::string ref_target = std::string(tr_h.substr(5));
                        auto ref_path = repo_root / ".git" / "modules" / node.path / ref_target;
                        if (fs::exists(ref_path, ec)) {
                            std::ifstream rf(ref_path);
                            std::string ref_line;
                            if (std::getline(rf, ref_line)) {
                                node.head_sha = std::string(trim(ref_line));
                            }
                        } else {
                            auto packed_file = repo_root / ".git" / "modules" / node.path / "packed-refs";
                            node.head_sha = resolve_packed(packed_file, ref_target);
                        }
                    } else {
                        node.head_sha = std::string(tr_h);
                    }
                }
            } else {
                node.head_sha = "UNINITIALIZED";
                node.status = AuditStatus::Uninitialized;
            }

            if (node.status == AuditStatus::Ok && node.index_sha != node.head_sha) {
                node.status = AuditStatus::CommitDrift;
            }

            const auto sub_dir = repo_root / node.path;
            node.detected_license = scan_spdx_directory(sub_dir);
            node.license_category = classify_license(node.detected_license);

            const auto nested_mod = sub_dir / ".gitmodules";
            if (fs::exists(nested_mod, ec)) {
                audit_recursive(sub_dir, node.path, depth + 1, nodes, visited);
            }
        }
        return {};
    }

    static void parse_index(const fs::path& index_path, const std::string& prefix, int depth, std::vector<SubmoduleNode>& nodes) {
        std::ifstream file(index_path, std::ios::binary);
        if (!file.is_open()) return;

        uint8_t hdr[12];
        if (!file.read(reinterpret_cast<char*>(hdr), 12)) return;

        uint32_t magic = parse_be32(std::span<const uint8_t, 4>(hdr, 4));
        uint32_t version = parse_be32(std::span<const uint8_t, 4>(hdr + 4, 4));
        uint32_t count = parse_be32(std::span<const uint8_t, 4>(hdr + 8, 4));

        if (magic != DIRC_MAGIC || version < 2 || version > 4) return;

        for (uint32_t i = 0; i < count; ++i) {
            uint8_t fixed[62];
            if (!file.read(reinterpret_cast<char*>(fixed), 62)) break;

            uint32_t mode = parse_be32(std::span<const uint8_t, 4>(fixed + 24, 4));
            uint16_t flags = (static_cast<uint16_t>(fixed[60]) << 8) | fixed[61];
            uint16_t name_len = flags & 0x0FFF;

            std::string path_str;
            if (name_len < 0x0FFF) {
                path_str.resize(name_len);
                file.read(path_str.data(), name_len);
            } else {
                std::getline(file, path_str, '\0');
            }

            size_t total = 62 + path_str.size();
            size_t pad = 8 - (total % 8);
            if (pad == 0) pad = 8;
            file.seekg(pad, std::ios::cur);

            if ((mode & 0170000) == MODE_GITLINK) {
                std::string full_path = prefix.empty() ? path_str : prefix + "/" + path_str;
                auto it = std::find_if(nodes.begin(), nodes.end(), [&](const auto& n) { return n.path == full_path; });
                if (it == nodes.end()) {
                    SubmoduleNode node;
                    node.path = std::move(full_path);
                    node.index_sha = hex_sha(std::span<const uint8_t, 20>(fixed + 40, 20));
                    node.in_index = true;
                    node.depth = depth;
                    nodes.push_back(std::move(node));
                } else {
                    it->index_sha = hex_sha(std::span<const uint8_t, 20>(fixed + 40, 20));
                    it->in_index = true;
                }
            }
        }
    }

    static void parse_modules(const fs::path& modules_path, const std::string& prefix, int depth, std::vector<SubmoduleNode>& nodes) {
        std::ifstream file(modules_path);
        std::string line, cur_path, cur_url;

        auto flush = [&]() {
            if (!cur_path.empty()) {
                std::string full_path = prefix.empty() ? cur_path : prefix + "/" + cur_path;
                auto it = std::find_if(nodes.begin(), nodes.end(), [&](const auto& n) { return n.path == full_path; });
                if (it == nodes.end()) {
                    SubmoduleNode node;
                    node.path = full_path;
                    node.url = cur_url;
                    node.in_gitmodules = true;
                    node.depth = depth;
                    nodes.push_back(std::move(node));
                } else {
                    it->url = cur_url;
                    it->in_gitmodules = true;
                }
                cur_path.clear();
                cur_url.clear();
            }
        };

        while (std::getline(file, line)) {
            auto tr = trim(line);
            if (tr.empty() || tr.starts_with('#') || tr.starts_with(';')) continue;

            if (tr.starts_with('[')) {
                flush();
                continue;
            }

            auto eq = tr.find('=');
            if (eq == std::string_view::npos) continue;

            auto k = trim(tr.substr(0, eq));
            auto v = trim(tr.substr(eq + 1));

            if (k == "path") cur_path = std::string(v);
            else if (k == "url") cur_url = std::string(v);
        }
        flush();
    }

    static std::string resolve_packed(const fs::path& packed_path, std::string_view ref_name) {
        std::ifstream file(packed_path);
        if (!file.is_open()) return "UNKNOWN_REF";

        std::string line;
        while (std::getline(file, line)) {
            auto tr = trim(line);
            if (tr.empty() || tr.starts_with('#') || tr.starts_with('^')) continue;

            auto sp = tr.find(' ');
            if (sp == std::string_view::npos) continue;

            auto sha = tr.substr(0, sp);
            auto name = trim(tr.substr(sp + 1));

            if (name == ref_name) return std::string(sha);
        }
        return "UNKNOWN_REF";
    }

    static std::string scan_spdx_directory(const fs::path& dir_path) {
        std::error_code ec;
        if (!fs::exists(dir_path, ec) || !fs::is_directory(dir_path, ec)) return "UNKNOWN";

        for (const auto& entry : fs::recursive_directory_iterator(dir_path, fs::directory_options::skip_permission_denied, ec)) {
            if (entry.is_regular_file()) {
                const auto ext = entry.path().extension().string();
                const auto name = entry.path().filename().string();

                if (ext == ".c" || ext == ".h" || ext == ".cpp" || ext == ".hpp" || ext == ".S" ||
                    name == "LICENSE" || name == "COPYING") {
                    auto lic = scan_spdx_file(entry.path());
                    if (lic != "UNKNOWN") return lic;
                }
            }
        }
        return "UNKNOWN";
    }

    static std::string scan_spdx_file(const fs::path& file_path) {
        std::ifstream f(file_path);
        if (!f.is_open()) return "UNKNOWN";

        std::string line;
        int count = 0;
        while (std::getline(f, line) && count < 100) {
            count++;
            auto pos = line.find("SPDX-License-Identifier:");
            if (pos != std::string::npos) {
                auto spdx_val = trim(line.substr(pos + 24));
                auto comment_end = spdx_val.find("*/");
                if (comment_end != std::string_view::npos) {
                    spdx_val = trim(spdx_val.substr(0, comment_end));
                }
                if (!spdx_val.empty()) return std::string(spdx_val);
            }
        }
        return "UNKNOWN";
    }

    static LicenseCategory classify_license(std::string_view lic) {
        if (lic.find("MIT") != std::string_view::npos ||
            lic.find("BSD") != std::string_view::npos ||
            lic.find("Apache") != std::string_view::npos ||
            lic.find("ISC") != std::string_view::npos ||
            lic.find("Zlib") != std::string_view::npos ||
            lic.find("Unlicense") != std::string_view::npos ||
            lic.find("CC0") != std::string_view::npos) {
            return LicenseCategory::Permissive;
        }
        if (lic.find("LGPL") != std::string_view::npos ||
            lic.find("MPL") != std::string_view::npos ||
            lic.find("CDDL") != std::string_view::npos ||
            lic.find("EPL") != std::string_view::npos) {
            return LicenseCategory::WeakCopyleft;
        }
        if (lic.find("GPL") != std::string_view::npos ||
            lic.find("AGPL") != std::string_view::npos ||
            lic.find("SSPL") != std::string_view::npos) {
            return LicenseCategory::StrongCopyleft;
        }
        return LicenseCategory::Unknown;
    }

    static std::string_view trim(std::string_view s) noexcept {
        auto start = s.find_first_not_of(" \t\r\n");
        if (start == std::string_view::npos) return {};
        auto end = s.find_last_not_of(" \t\r\n");
        return s.substr(start, end - start + 1);
    }
};

} // namespace auditor

int main(int argc, char** argv) {
    fs::path repo_root = (argc > 1) ? argv[1] : ".";

    auto result = auditor::SubmoduleTreeAuditor::audit_tree(repo_root);
    if (!result) {
        std::cerr << "Audit failed with internal error\n";
        return 1;
    }

    auditor::SubmoduleTreeAuditor::print_report(*result);
    auditor::SubmoduleTreeAuditor::export_sbom("submodule-audit.json", *result);

    bool has_critical = false;
    for (const auto& node : *result) {
        if (node.status != auditor::AuditStatus::Ok || node.license_category == auditor::LicenseCategory::StrongCopyleft) {
            has_critical = true;
            break;
        }
    }

    return has_critical ? 1 : 0;
}
