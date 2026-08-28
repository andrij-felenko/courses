#!/bin/sh
# .git/hooks/pre-commit — локальна валідація архітектури
echo "🔍 Перевірка архітектурних інваріантів C4..."
structurizr export -w architecture/workspace.dsl -f json -o architecture/output/
python architecture/validator.py architecture/output/workspace.json

if [ $? -ne 0 ]; then
    echo "❌ Комміт відхилено: виявлено порушення архітектурних правил!"
    exit 1
fi
