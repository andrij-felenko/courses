#!/usr/bin/env bash
set -euo pipefail

# 1. Малюємо Mermaid з ЄДИНОГО джерела у тимчасову теку.
#    Нова консолідована тула Structurizr (Spring Boot .war):
java -jar structurizr.war export -workspace workspace.dsl -format mermaid -output build/diagrams
#    (застаріла, але ще жива команда CLI:
#     ./structurizr.sh export -workspace workspace.dsl -format mermaid -output build/diagrams)

# 2. Порівнюємо згенероване з тим, що закоммічено. Будь-яка різниця — стоп.
if ! diff -r build/diagrams docs/diagrams; then
  echo "Діаграми застаріли: перегенеруй і закоммить docs/diagrams" >&2
  exit 1
fi
