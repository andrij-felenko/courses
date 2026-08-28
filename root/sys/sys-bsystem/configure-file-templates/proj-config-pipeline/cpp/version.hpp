// include/diag/version.hpp.in — шаблон типізованих метаданих версії C++
#pragma once

#include <cstdint>
#include <string_view>

namespace diag::version {

// Текстова назва проєкту, отримана з директиви project(...)
inline constexpr std::string_view project_name{"@PROJECT_NAME@"};

// Повний семантичний рядок версії (наприклад "2.4.1")
inline constexpr std::string_view version_string{"@PROJECT_VERSION@"};

// Коротка ревізія коміту Git
inline constexpr std::string_view git_commit_hash{"@DIAG_GIT_HASH@"};

// Ім'я активної гілки Git
inline constexpr std::string_view git_branch{"@DIAG_GIT_BRANCH@"};

// Числові складові версії для програмного порівняння в if constexpr
inline constexpr std::uint32_t major{@PROJECT_VERSION_MAJOR@};
inline constexpr std::uint32_t minor{@PROJECT_VERSION_MINOR@};
inline constexpr std::uint32_t patch{@PROJECT_VERSION_PATCH@};

// Ознака того, що бінарний файл зібрано з модифікованого робочого дерева
inline constexpr bool is_dirty_tree{@DIAG_GIT_DIRTY_FLAG@};

} // namespace diag::version
