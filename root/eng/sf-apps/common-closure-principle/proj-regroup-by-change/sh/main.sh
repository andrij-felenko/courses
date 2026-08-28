mkdir -p src/tax src/shipping src/discount

# 1. ЛИШЕ перенос — жодного рядка не чіпаємо
for axis in tax shipping discount; do
  git mv "src/validation/$axis-rules.ts"  "src/$axis/rules.ts"
  git mv "src/presentation/$axis-view.ts" "src/$axis/view.ts"
  git mv "src/persistence/$axis-repo.ts"  "src/$axis/repo.ts"
done
git commit -m "move: компоненти за віссю зміни (лише перенос, без правок)"

# 2. ОКРЕМИМ комітом — полагодити шляхи імпортів
#    ../validation/tax-rules → ./rules  тощо
git commit -am "fix: шляхи імпортів після переносу"
