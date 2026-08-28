# Тест 1: Валідний коміт з описом та підписом
cat << 'EOF' | ./dco_verifier "Ivan Petrenko" "ivan@example.org"
fix(core): resolve memory leak in worker thread pool

Signed-off-by: Ivan Petrenko <ivan@example.org>
EOF
# Очікуваний вивід: {"valid":true,"status":"ok",...}, код 0

# Тест 2: Підпис всередині опису без фінального блоку трейлерів
cat << 'EOF' | ./dco_verifier "Ivan Petrenko" "ivan@example.org"
docs: update readme with example:
Here is a sample trailer:
Signed-off-by: Ivan Petrenko <ivan@example.org>

This commit updates documentation.
EOF
# Очікуваний вивід: {"valid":false,"error":"missing_signed_off_by",...}, код 1
