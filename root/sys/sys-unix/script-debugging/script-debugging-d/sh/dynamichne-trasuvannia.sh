#!/usr/bin/env bash
set -euo pipefail

backup_dir="/var/backups/cluster"
service_name="auth-api"
archive_name="${service_name}_$(date +%Y%m%d).tar.gz"

set -x  # Вмикаємо трасування для критичної секції
mkdir -p "${backup_dir}"
tar -czf "${backup_dir}/${archive_name}" -C "/etc/${service_name}" conf.d
set +x  # Вимикаємо трасування
