# 1. Звичайна інсталяція в сконфігурований CMAKE_INSTALL_PREFIX (за замовчуванням /usr/local)
cmake --install build

# 2. Інсталяція з тимчасовою зміною префікса без перекомпіляції
cmake --install build --prefix /opt/myapp

# 3. Інсталяція з очищенням налагоджувальних символів (strip)
cmake --install build --prefix /usr --strip

# 4. Інсталяція в ізольований каталог пакувальника через змінну DESTDIR
DESTDIR=/tmp/staging-pkg cmake --install build
