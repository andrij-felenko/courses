#pragma once

#include <cstddef>
#include <filesystem>

// Дії над деревом монтувань: підготовка й перенесення службових гілок
// зі старого кореня в новий (крок 1 фази 5).
namespace boot::mounts {

// Знімає з усього дерева спільне поширення (shared). Без цього MS_MOVE
// відмовляє з EINVAL. Кидає std::system_error: без цього кроку далі нікуди.
void make_tree_private();

// Переставляє /dev, /proc, /sys та /run зі старого кореня всередину
// new_root. Демонтувати їх не можна: на них тримаються відкриті дескриптори
// й активні структури ядра. Повертає кількість тих, що не переїхали.
std::size_t move_special(const std::filesystem::path& new_root);

// Точка монтування лежить на іншому пристрої, ніж її батьківський каталог.
bool is_mount_point(const std::filesystem::path& path);

}  // namespace boot::mounts
