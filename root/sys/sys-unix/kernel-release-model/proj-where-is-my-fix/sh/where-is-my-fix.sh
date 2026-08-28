#!/bin/sh
# where-is-my-fix.sh — у які стабільні випуски доїхало виправлення з mainline.
# Запускати в клоні stable/linux.git. Аргумент — хеш коміту з mainline.
set -u

full=$(git rev-parse --verify "$1^{commit}") || exit 1
printf 'mainline: %s\n\n' \
       "$(git describe --contains "$full" 2>/dev/null || echo 'ще в жодному тезі')"

git branch -r --list 'origin/linux-*.y' | tr -d ' ' | while read -r branch; do
    tag=v${branch#origin/linux-}          # origin/linux-6.12.y → v6.12.y
    tag=${tag%.y}                         #                     → v6.12
    git rev-parse --verify --quiet "$tag^{commit}" >/dev/null || continue

    # Гілка молодша за виправлення — воно вже в її основі, переносити нічого.
    if git merge-base --is-ancestor "$full" "$branch"; then
        printf '%-16s в основі гілки\n' "${branch#origin/}"
        continue
    fi

    # Інакше шукаємо перенесення за повним хешем у тілі повідомлення.
    port=$(git log -1 --fixed-strings --grep="$full" --format='%H' "$tag..$branch")
    if [ -n "$port" ]; then
        printf '%-16s %.12s → %s\n' "${branch#origin/}" "$port" \
               "$(git describe --contains "$port" 2>/dev/null || echo 'ще не в тезі')"
    else
        printf '%-16s не знайдено\n' "${branch#origin/}"
    fi
done
