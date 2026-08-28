set -o pipefail
pytest tests/ --junitxml=reports/junit.xml
rc=$?

case "$rc" in
  0) echo "усі перевірки пройшли" ;;
  1) echo "є падіння — не пускати";                       exit 1 ;;
  5) echo "жоден тест не зібрано: вибірка порожня";        exit 1 ;;
  *) echo "прогін не відбувся (код $rc) — не пускати";     exit 1 ;;
esac
