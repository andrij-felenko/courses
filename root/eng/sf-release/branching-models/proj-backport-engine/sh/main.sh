#!/usr/bin/env bash
# Git pre-receive hook: Валідація бекпортів перед записом у репозиторій

set -euo pipefail

while read -r oldrev newrev refname; do
    if [[ "$refname" =~ ^refs/heads/support/ ]]; then
        # Перевірка кожного нового коміту в діапазоні
        for commit in $(git rev-list "$oldrev..$newrev"); do
            git log -1 --stat "$commit" | /usr/local/bin/backport-inspector || {
                echo "ПОМИЛКА: Коміт $commit відхилено валідатором бекпортів." >&2
                echo "Переконайтеся у наявності [vX.Y] префікса, Upstream SHA та допустимому розмірі diff." >&2
                exit 1
            }
        done
    fi
done
