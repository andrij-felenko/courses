# 1. Валідація метаданих Pull Request на відповідність фазі Code Freeze
rc-arbiter validate-pr \
  --policy .ci/release-gate.yaml \
  --pr-metadata pr-1042.json \
  --diff patch.diff

# 2. Оцінка розмірів секцій скомпільованого бінарника за мапою лінкера
rc-arbiter evaluate-budgets \
  --policy .ci/release-gate.yaml \
  --map-file build/firmware.map \
  --elf-file build/firmware.elf

# 3. Комплексна верифікація звітів тестування та генерація маніфесту
rc-arbiter verify-candidate \
  --policy .ci/release-gate.yaml \
  --hil-report test-results/hil-summary.json \
  --soak-report test-results/soak-72h.json \
  --artifact build/firmware.bin \
  --out-manifest build/rc-manifest.json

# 4. Промоція кандидата у фінальний Golden Master через криптографічний HSM-модуль
rc-arbiter promote-to-ga \
  --manifest build/rc-manifest.json \
  --hsm-slot 1 \
  --key-alias "prod-firmware-signing-2026" \
  --output-package dist/firmware-v2.4.0-GA.tar.gz
