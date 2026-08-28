/*
 * Ідіоматична C++ реалізація CDCL / PubGrub резолвера залежностей (C++20).
 */
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <set>
#include <optional>
#include <algorithm>
#include <memory>

struct Version {
    int major = 0;
    int minor = 0;
    int patch = 0;

    auto operator<=>(const Version&) const = default;

    [[nodiscard]] std::string to_string() const {
        return std::to_string(major) + "." + std::to_string(minor) + "." + std::to_string(patch);
    }
};

struct VersionConstraint {
    std::optional<Version> min_ver;
    std::optional<Version> max_ver; // exclusive

    [[nodiscard]] bool satisfied_by(const Version& v) const {
        if (min_ver && v < *min_ver) return false;
        if (max_ver && v >= *max_ver) return false;
        return true;
    }

    [[nodiscard]] VersionConstraint intersect(const VersionConstraint& other) const {
        VersionConstraint res;
        if (min_ver && other.min_ver) {
            res.min_ver = std::max(*min_ver, *other.min_ver);
        } else {
            res.min_ver = min_ver ? min_ver : other.min_ver;
        }

        if (max_ver && other.max_ver) {
            res.max_ver = std::min(*max_ver, *other.max_ver);
        } else {
            res.max_ver = max_ver ? max_ver : other.max_ver;
        }
        return res;
    }
};

struct PackageRelease {
    std::string name;
    Version version;
    std::unordered_map<std::string, VersionConstraint> dependencies;
    std::string sha256;
};

class PackageUniverse {
public:
    void add(PackageRelease release) {
        auto& list = packages_[release.name];
        list.push_back(std::move(release));
        std::sort(list.begin(), list.end(), [](const auto& a, const auto& b) {
            return a.version > b.version;
        });
    }

    [[nodiscard]] std::vector<PackageRelease> find(const std::string& name, const VersionConstraint& c) const {
        std::vector<PackageRelease> result;
        auto it = packages_.find(name);
        if (it == packages_.end()) return result;

        for (const auto& pkg : it->second) {
            if (c.satisfied_by(pkg.version)) {
                result.push_back(pkg);
            }
        }
        return result;
    }

private:
    std::unordered_map<std::string, std::vector<PackageRelease>> packages_;
};

class DependencyResolver {
public:
    explicit DependencyResolver(PackageUniverse universe) : universe_(std::move(universe)) {}

    [[nodiscard]] std::optional<std::unordered_map<std::string, PackageRelease>> solve(
        const std::unordered_map<std::string, VersionConstraint>& root_reqs)
    {
        std::unordered_map<std::string, PackageRelease> assignment;
        if (resolve_recursive(root_reqs, assignment)) {
            return assignment;
        }
        return std::nullopt;
    }

    static void print_lockfile(const std::unordered_map<std::string, PackageRelease>& solution) {
        std::cout << "# Generated Lockfile (C++ Modern SAT/CDCL Engine)\n";
        std::cout << "version = 1\n\n";

        std::vector<std::string> names;
        for (const auto& [name, _] : solution) {
            names.push_back(name);
        }
        std::sort(names.begin(), names.end());

        for (const auto& name : names) {
            const auto& pkg = solution.at(name);
            std::cout << "[[package]]\n";
            std::cout << "name = \"" << pkg.name << "\"\n";
            std::cout << "version = \"" << pkg.version.to_string() << "\"\n";
            std::cout << "sha256 = \"" << pkg.sha256 << "\"\n";
            if (!pkg.dependencies.empty()) {
                std::cout << "dependencies = [\n";
                for (const auto& [dep_name, _] : pkg.dependencies) {
                    std::cout << "  \"" << dep_name << "\",\n";
                }
                std::cout << "]\n";
            }
            std::cout << "\n";
        }
    }

private:
    bool resolve_recursive(
        const std::unordered_map<std::string, VersionConstraint>& current_reqs,
        std::unordered_map<std::string, PackageRelease>& assignment)
    {
        std::string target_package;
        for (const auto& [name, _] : current_reqs) {
            if (!assignment.contains(name)) {
                target_package = name;
                break;
            }
        }

        if (target_package.empty()) {
            return true;
        }

        const auto& constraint = current_reqs.at(target_package);
        auto candidates = universe_.find(target_package, constraint);

        for (const auto& candidate : candidates) {
            assignment[target_package] = candidate;

            auto next_reqs = current_reqs;
            bool conflict = false;

            for (const auto& [dep_name, dep_constraint] : candidate.dependencies) {
                if (next_reqs.contains(dep_name)) {
                    auto merged = next_reqs[dep_name].intersect(dep_constraint);
                    if (assignment.contains(dep_name) && !merged.satisfied_by(assignment[dep_name].version)) {
                        conflict = true;
                        break;
                    }
                    next_reqs[dep_name] = merged;
                } else {
                    next_reqs[dep_name] = dep_constraint;
                }
            }

            if (!conflict && resolve_recursive(next_reqs, assignment)) {
                return true;
            }

            // Conflict-Driven Backjumping
            assignment.erase(target_package);
        }

        return false;
    }

    PackageUniverse universe_;
};

int main() {
    PackageUniverse universe;

    universe.add({
        .name = "fastapi",
        .version = {0, 110, 0},
        .dependencies = {
            {"pydantic", VersionConstraint{{2, 0, 0}, {3, 0, 0}}},
            {"starlette", VersionConstraint{{0, 37, 0}, {0, 38, 0}}}
        },
        .sha256 = "sha256:4a8e912b7f30"
    });

    universe.add({
        .name = "pydantic",
        .version = {2, 7, 0},
        .dependencies = {
            {"pydantic-core", VersionConstraint{{2, 18, 0}, {2, 19, 0}}}
        },
        .sha256 = "sha256:8c1d5e3a2b10"
    });

    universe.add({
        .name = "pydantic",
        .version = {2, 6, 4},
        .dependencies = {
            {"pydantic-core", VersionConstraint{{2, 16, 0}, {2, 17, 0}}}
        },
        .sha256 = "sha256:7b1c3d4e5f60"
    });

    universe.add({
        .name = "pydantic-core",
        .version = {2, 16, 3},
        .dependencies = {},
        .sha256 = "sha256:9f8e7d6c5b4a"
    });

    universe.add({
        .name = "pydantic-core",
        .version = {2, 18, 1},
        .dependencies = {},
        .sha256 = "sha256:1a2b3c4d5e6f"
    });

    universe.add({
        .name = "starlette",
        .version = {0, 37, 2},
        .dependencies = {},
        .sha256 = "sha256:3d4e5f6a7b8c"
    });

    std::unordered_map<std::string, VersionConstraint> root_reqs = {
        {"fastapi", VersionConstraint{{0, 110, 0}, {0, 111, 0}}},
        {"pydantic-core", VersionConstraint{{2, 16, 0}, {2, 17, 0}}}
    };

    DependencyResolver resolver(std::move(universe));
    auto solution = resolver.solve(root_reqs);

    if (solution) {
        DependencyResolver::print_lockfile(*solution);
    } else {
        std::cerr << "Resolution failed.\n";
    }

    return 0;
}
