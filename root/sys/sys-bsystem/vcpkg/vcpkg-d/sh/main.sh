# 1. Локальний файловий кеш на спільному мережевому диску
export VCPKG_BINARY_SOURCES="clear;files,/mnt/shared/vcpkg-cache,readwrite"

# 2. Кеш GitHub Actions у хмарі
export VCPKG_BINARY_SOURCES="clear;gha,readwrite"

# 3. Віддалений HTTP/REST сервер або корпоративний Nexus/Artifactory
export VCPKG_BINARY_SOURCES="clear;http,https://artifacts.company.internal/vcpkg/{name}/{version}/{sha}.zip,readwrite"

# 4. Репозиторій пакетів NuGet
export VCPKG_BINARY_SOURCES="clear;nuget,https://pkgs.dev.azure.com/org/_packaging/feed/nuget/v3/index.json,readwrite"
