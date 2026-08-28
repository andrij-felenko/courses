#!/usr/bin/env bash
# Непереносний варіант: використовує розширення GNU Bash
set -euo pipefail

declare -A SERVICES=( [nginx]="/var/log/nginx" [db]="/var/log/postgresql" )
declare -a LOG_FILES=()

read_logs() {
    local svc=$1
    local dir=${SERVICES[$svc]}
    
    [[ -d "$dir" ]] || { echo "Пропуск $svc: нема каталогу"; return 0; }
    
    while IFS= read -r -d '' file; do
        LOG_FILES+=("$file")
    done < <(find "$dir" -maxdepth 1 -name "*.log" -print0)
}

for s in "${!SERVICES[@]}"; do
    read_logs "$s"
done

echo -n "Знайдено файлів: ${#LOG_FILES[@]} ... "
grep -P '^\d{4}-\d{2}-\d{2}.*(ERROR|FATAL)' "${LOG_FILES[@]}" \
    | sed -i 's/token=[^ ]+/token=***/g' report.txt
echo "Завершено."
