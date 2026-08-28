// git_index_submodule_auditor.cpp — Прямий двійковий парсер .git/index та .gitmodules на C++20
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

namespace fs = std::filesystem;

namespace git_binary {

constexpr uint32_t DIRC_MAGIC = 0x44495243;
constexpr uint32_t MODE_GITLINK = 0160000;

struct SubmoduleAuditEntry {
    std::string path;
    std::string url;
    std::string index_sha;
    std::string head_sha;
    bool in_gitmodules{false};
    bool in_index{false};
    bool is_synchronized{false};
};

enum class AuditError {
    FileNotFound,
    InvalidMagic,
    UnsupportedVersion,
    CorruptedData
};

class IndexAuditor {
public:
    static uint32_t parse_be32(std::span<const uint8_t, 4> bytes) noexcept {
        return (static_cast<uint32_t>(bytes[0]) << 24) |
               (static_cast<uint32_t>(bytes[1]) << 16) |
               (static_cast<uint32_t>(bytes[2]) << 8)  |
               (static_cast<uint32_t>(bytes[3]));
    }

    static std::string format_hex_sha(std::span<const uint8_t, 20> sha) {
        std::string hex;
        hex.reserve(40);
        for (uint8_t byte : sha) {
            hex += std::format("{:02x}", byte);
        }
        return hex;
    }

    static std::expected<std::vector<SubmoduleAuditEntry>, AuditError>
    audit_repository(const fs::path& repo_root) {
        const auto index_path = repo_root / ".git" / "index";
        const auto modules_path = repo_root / ".gitmodules";

        if (!fs::exists(index_path)) {
            return std::unexpected(AuditError::FileNotFound);
        }

        std::ifstream file(index_path, std::ios::binary);
        if (!file.is_open()) {
            return std::unexpected(AuditError::FileNotFound);
        }

        uint8_t hdr[12];
        if (!file.read(reinterpret_cast<char*>(hdr), 12)) {
            return std::unexpected(AuditError::CorruptedData);
        }

        uint32_t magic = parse_be32(std::span<const uint8_t, 4>(hdr, 4));
        uint32_t version = parse_be32(std::span<const uint8_t, 4>(hdr + 4, 4));
        uint32_t entries_count = parse_be32(std::span<const uint8_t, 4>(hdr + 8, 4));

        if (magic != DIRC_MAGIC) return std::unexpected(AuditError::InvalidMagic);
        if (version < 2 || version > 4) return std::unexpected(AuditError::UnsupportedVersion);

        std::vector<SubmoduleAuditEntry> results;

        for (uint32_t i = 0; i < entries_count; ++i) {
            uint8_t fixed[62];
            if (!file.read(reinterpret_cast<char*>(fixed), 62)) break;

            uint32_t mode = parse_be32(std::span<const uint8_t, 4>(fixed + 24, 4));
            uint16_t flags = (static_cast<uint16_t>(fixed[60]) << 8) | fixed[61];
            uint16_t name_len = flags & 0x0FFF;

            std::string entry_path;
            if (name_len < 0x0FFF) {
                entry_path.resize(name_len);
                file.read(entry_path.data(), name_len);
            } else {
                std::getline(file, entry_path, '\0');
            }

            size_t total = 62 + entry_path.size();
            size_t pad = 8 - (total % 8);
            if (pad == 0) pad = 8;
            file.seekg(pad, std::ios::cur);

            if ((mode & 0170000) == MODE_GITLINK) {
                SubmoduleAuditEntry entry;
                entry.path = std::move(entry_path);
                entry.index_sha = format_hex_sha(std::span<const uint8_t, 20>(fixed + 40, 20));
                entry.in_index = true;
                results.push_back(std::move(entry));
            }
        }

        // Парсинг .gitmodules та зіставлення з HEAD
        if (fs::exists(modules_path)) {
            parse_modules_config(modules_path, results);
        }

        verify_local_heads(repo_root, results);
        return results;
    }

private:
    static void parse_modules_config(const fs::path& modules_path, std::vector<SubmoduleAuditEntry>& entries) {
        std::ifstream file(modules_path);
        std::string line;
        std::string cur_path, cur_url;

        auto apply_record = [&]() {
            if (!cur_path.empty()) {
                auto it = std::find_if(entries.begin(), entries.end(),
                                       [&](const auto& e) { return e.path == cur_path; });
                if (it != entries.end()) {
                    it->url = cur_url;
                    it->in_gitmodules = true;
                } else {
                    SubmoduleAuditEntry new_e;
                    new_e.path = cur_path;
                    new_e.url = cur_url;
                    new_e.in_gitmodules = true;
                    entries.push_back(std::move(new_e));
                }
                cur_path.clear();
                cur_url.clear();
            }
        };

        while (std::getline(file, line)) {
            auto trimmed = trim(line);
            if (trimmed.empty() || trimmed.starts_with('#')) continue;

            if (trimmed.starts_with('[')) {
                apply_record();
                continue;
            }

            auto eq = trimmed.find('=');
            if (eq == std::string_view::npos) continue;

            auto key = trim(trimmed.substr(0, eq));
            auto val = trim(trimmed.substr(eq + 1));

            if (key == "path") cur_path = std::string(val);
            else if (key == "url") cur_url = std::string(val);
        }
        apply_record();
    }

    static void verify_local_heads(const fs::path& repo_root, std::vector<SubmoduleAuditEntry>& entries) {
        for (auto& entry : entries) {
            const auto head_file_path = repo_root / ".git" / "modules" / entry.path / "HEAD";
            std::error_code ec;
            if (fs::exists(head_file_path, ec)) {
                std::ifstream head_file(head_file_path);
                std::string head_line;
                if (std::getline(head_file, head_line)) {
                    entry.head_sha = std::string(trim(head_line));
                }
            } else {
                entry.head_sha = "UNINITIALIZED";
            }
            entry.is_synchronized = (!entry.index_sha.empty() && entry.index_sha == entry.head_sha);
        }
    }

    static std::string_view trim(std::string_view s) noexcept {
        auto start = s.find_first_not_of(" \t\r\n");
        if (start == std::string_view::npos) return {};
        auto end = s.find_last_not_of(" \t\r\n");
        return s.substr(start, end - start + 1);
    }
};

} // namespace git_binary
