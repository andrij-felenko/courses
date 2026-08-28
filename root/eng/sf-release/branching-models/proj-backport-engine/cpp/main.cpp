#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <sstream>
#include <algorithm>
#include <charconv>

namespace release::backport {

enum class ValidationError {
    MissingUpstreamSha,
    MissingBranchPrefix,
    DiffLimitExceeded,
    InvalidStructure
};

struct CommitMetadata {
    std::string target_branch;
    std::string upstream_sha;
    std::string subject;
    int lines_added{0};
    int lines_deleted{0};
    int files_changed{0};
};

class BackportInspector {
public:
    static constexpr int MaxSafeLineDiff = 300;

    [[nodiscard]] static auto parse(std::string_view raw_commit_log) 
        -> std::pair<std::optional<CommitMetadata>, std::optional<ValidationError>> 
    {
        CommitMetadata meta;
        std::istringstream stream{std::string(raw_commit_log)};
        std::string line;
        bool header_parsed = false;

        while (std::getline(stream, line)) {
            trim(line);
            if (line.empty()) continue;

            if (!header_parsed) {
                meta.subject = line;
                header_parsed = true;

                if (line.starts_with('[') && line.find(']') != std::string::npos) {
                    const auto end_idx = line.find(']');
                    meta.target_branch = line.substr(1, end_idx - 1);
                } else {
                    return {std::nullopt, ValidationError::MissingBranchPrefix};
                }
                continue;
            }

            if (meta.upstream_sha.empty()) {
                if (auto sha = extract_sha(line, "(cherry picked from commit "); sha) {
                    meta.upstream_sha = *sha;
                } else if (auto sha_up = extract_sha(line, "Upstream-commit: "); sha_up) {
                    meta.upstream_sha = *sha_up;
                }
            }

            parse_diffstat(line, meta);
        }

        if (meta.upstream_sha.empty()) {
            return {std::nullopt, ValidationError::MissingUpstreamSha};
        }

        if (meta.lines_added + meta.lines_deleted > MaxSafeLineDiff) {
            return {std::nullopt, ValidationError::DiffLimitExceeded};
        }

        return {meta, std::nullopt};
    }

private:
    static void trim(std::string& s) {
        s.erase(s.find_last_not_of(" \r\n\t") + 1);
    }

    static auto extract_sha(std::string_view line, std::string_view prefix) -> std::optional<std::string> {
        const auto pos = line.find(prefix);
        if (pos == std::string_view::npos) return std::nullopt;

        auto rest = line.substr(pos + prefix.size());
        if (const auto end_bracket = rest.find(')'); end_bracket != std::string_view::npos) {
            rest = rest.substr(0, end_bracket);
        }
        if (rest.size() >= 7) {
            return std::string(rest);
        }
        return std::nullopt;
    }

    static void parse_diffstat(std::string_view line, CommitMetadata& meta) {
        if (line.find("file changed") == std::string_view::npos && 
            line.find("files changed") == std::string_view::npos) {
            return;
        }

        std::istringstream ls{std::string(line)};
        std::string token;
        while (ls >> token) {
            if (token.find("insertion") != std::string::npos) {
                // обробка токена
            }
        }
        
        if (const auto p_ins = line.find("insertion"); p_ins != std::string_view::npos) {
            const auto space_before = line.rfind(' ', p_ins - 2);
            if (space_before != std::string_view::npos) {
                std::from_chars(line.data() + space_before + 1, line.data() + p_ins - 1, meta.lines_added);
            }
        }
        if (const auto p_del = line.find("deletion"); p_del != std::string_view::npos) {
            const auto space_before = line.rfind(' ', p_del - 2);
            if (space_before != std::string_view::npos) {
                std::from_chars(line.data() + space_before + 1, line.data() + p_del - 1, meta.lines_deleted);
            }
        }
    }
};

} // namespace release::backport

int main() {
    constexpr std::string_view sample_commit = 
        "[v2.4] fix(io): prevent file descriptor leak during ring reset\n"
        "\n"
        "Under high packet rates, resetting the descriptor ring failed to close\n"
        "pending eventfds, leading to exhaustion of process handles.\n"
        "\n"
        "(cherry picked from commit 8f4a21b3c990a174f82d1c9b3a0e4123456789ab)\n"
        "Fixes: CVE-2026-1940\n"
        "---\n"
        " 2 files changed, 14 insertions(+), 3 deletions(-)\n";

    const auto [meta, err] = release::backport::BackportInspector::parse(sample_commit);

    if (meta.has_value()) {
        std::cout << "STATUS: VALID BACKPORT (C++20)\n";
        std::cout << "Target Branch : " << meta->target_branch << "\n";
        std::cout << "Upstream SHA  : " << meta->upstream_sha << "\n";
        std::cout << "Lines Changed : +" << meta->lines_added << " / -" << meta->lines_deleted << "\n";
        return 0;
    }

    std::cerr << "VALIDATION FAILED: Code " << static_cast<int>(*err) << "\n";
    return 1;
}
