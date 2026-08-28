# 1. Rust Cargo
# Перериває роботу з кодом помилки, якщо Cargo.lock відсутній або вимагає оновлення
cargo build --locked

# 2. Node.js / npm
# Видаляє node_modules, встановлює суворо за package-lock.json і падає, якщо замок розходиться з package.json
npm ci

# 3. pnpm / yarn
pnpm install --frozen-lockfile
yarn install --immutable

# 4. Conan 2.0
# Забороняє додавати нові вузли чи змінювати ревізії у conan.lock
conan install . --lockfile=conan.lock --lockfile-partial=False
