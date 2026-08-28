# Провести повний аудит кодової бази та логів запитів PostgreSQL
dh-audit-cli scan \
  --config=./audit-config.json \
  --repo-path=/src/digital-homes-monolith \
  --pg-log-path=/var/log/postgresql/postgresql-query.log \
  --output=json \
  --report-file=./service-audit-report.json

# Перевірити дотримання архітектурних меж у CI/CD (повертає exit code 1 при порушеннях)
dh-audit-cli check-boundaries \
  --config=./audit-config.json \
  --max-allowed-cross-joins=0 \
  --fail-on-critical
