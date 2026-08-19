/* reference/build-systems/manifest.js — ДОВІДНИК «Системи збірки» (тип "reference").
   Довідник — 4-й вид книги (AUTHORING §1): рукотворна система з версіями й синтаксисом.
   Схема — як у book (§2 v6): sections[] → topics[], статус на КОЖНУ версію.

   МЕЖА З book/programming (§1): «Компіляція», «Лінкування», «Стадії компілятора» вже написані
   в book/programming/languages як загальні принципи — тут їх НЕ дублюємо. Сюди йде те,
   до чого доречне «а в якій версії?»: мова CMakeLists, менеджери пакетів, тулчейни.

   Android — свідомо ОБАБІЧ і коротко (розділ `toolchains`): лише нюанси третьої платформи,
   без окремого довідника, поки Linux і CMake не наповнені.

   31 тема у 4 розділах. Усі заведено як detailed:pending (basic — за потреби, §3). */
(window.__BOOKS__ = window.__BOOKS__ || []).push({
  type: "reference", slug: "build-systems", title: "Системи збірки",
  sections: [
    { slug: "fundamentals", title: "Що робить система збірки", scope: "Модель, спільна для всіх систем збірки: граф, актуальність, відтворюваність.",
      topics: [
        { slug: "build-system-role", title: "Роль системи збірки: від дерева файлів до артефакту", basic: { status: "empty" }, detailed: { status: "done" } , hist: [{ file: "hist-make-birth.md", status: "done" }] , math: [{ file: "math-rebuild-cost.md", status: "done" }] , proj: [{ file: "proj-mini-build.md", status: "done" }] },
        { slug: "dependency-graph", title: "Граф залежностей і порядок робіт", basic: { status: "empty" }, detailed: { status: "recheck" } },
        { slug: "incremental-build", title: "Інкрементальна збірка: як вирішують, що застаріло", basic: { status: "empty" }, detailed: { status: "done" } , api: [{ file: "api-depfile.md", status: "done" }] , math: [{ file: "math-early-cutoff.md", status: "done" }] },
        { slug: "configure-and-generate", title: "Конфігурація, генерація і збірка поза деревом джерел", basic: { status: "empty" }, detailed: { status: "recheck" } , "hist": [{ file: "hist-meta-build.md", status: "recheck" }] },
        { slug: "reproducible-builds", title: "Відтворювані збірки", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-repro-flags.md", status: "recheck" }] , "hist": [{ file: "hist-reproducible-builds.md", status: "recheck" }] , "proj": [{ file: "proj-repro-check.md", status: "recheck" }] },
        { slug: "build-speed", title: "Швидкість збірки: Ninja, ccache, PCH, unity", basic: { status: "empty" }, detailed: { status: "recheck" } },
      ] },

    { slug: "cmake", title: "CMake", scope: "Мова, модель цілей і практика CMake — системи збірки більшості сучасних C++-проєктів.",
      topics: [
        { slug: "cmake-language", title: "Мова CMakeLists: змінні, області, потік керування", basic: { status: "empty" }, detailed: { status: "done" } , hist: [{ file: "hist-cmake-language.md", status: "done" }] , api: [{ file: "api-if-and-lists.md", status: "done" }] , proj: [{ file: "proj-helper-function.md", status: "done" }] },
        { slug: "targets-and-properties", title: "Цілі й властивості замість глобальних змінних", basic: { status: "empty" }, detailed: { status: "done" } , hist: [{ file: "hist-target-turn.md", status: "done" }] , api: [{ file: "api-target-properties.md", status: "done" }] },
        { slug: "usage-requirements", title: "Вимоги вжитку: PUBLIC, PRIVATE, INTERFACE", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-usage-requirements.md", status: "recheck" }] },
        { slug: "find-package", title: "find_package: Config проти Module й імпортовані цілі", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-find-package.md", status: "recheck" }] , "proj": [{ file: "proj-find-module.md", status: "recheck" }] },
        { slug: "fetchcontent-subprojects", title: "FetchContent і підпроєкти: чужий код усередині збірки", basic: { status: "empty" }, detailed: { status: "recheck" } },
        { slug: "generator-expressions", title: "Генераторні вирази: рішення, відкладене до генерації", basic: { status: "empty" }, detailed: { status: "recheck" } },
        { slug: "cmake-presets", title: "CMakePresets: конфігурації як декларація", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-presets-schema.md", status: "recheck" }] , "hist": [{ file: "hist-cmake-presets.md", status: "recheck" }] },
        { slug: "cache-and-options", title: "Кеш CMake, опції та їхнє життя між прогонами", basic: { status: "empty" }, detailed: { status: "recheck" } , "api": [{ file: "api-cache-commands.md", status: "recheck" }] , "proj": [{ file: "proj-cache-presets.md", status: "recheck" }] },
        { slug: "custom-commands", title: "Власні команди й цілі: кодогенерація у збірці", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "ctest", title: "CTest: реєстрація й запуск тестів", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "install-and-export", title: "install і export: зробити проєкт придатним для find_package", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "cpack", title: "CPack: збірка дистрибутива", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "cmake-toolchain-file", title: "Файл тулчейна: як CMake дізнається про чужу платформу", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "cmake-antipatterns", title: "Антипатерни CMake і чому вони живучі", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "configure-file-templates", title: "configure_file: значення конфігурації у згенерованих файлах", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "cmake-policies", title: "Політики CMake: як мова змінюється, не ламаючи старі проєкти", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },

    { slug: "dependencies", title: "Залежності", scope: "Як проєкт отримує чужий код відтворювано й однаково на всіх машинах.",
      topics: [
        { slug: "dependency-manager-model", title: "Модель менеджера залежностей C++", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "conan", title: "Conan: рецепти, профілі, бінарні пакети", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "vcpkg", title: "vcpkg: порти, тріплети, маніфестний режим", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "vendoring-submodules", title: "Вендоринг і git-сабмодулі", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "version-pinning", title: "Закріплення версій і замки залежностей", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },

    { slug: "toolchains", title: "Тулчейни й чужі платформи", scope: "Компілятори та крос-компіляція: де три платформи розходяться. Android — коротко, лише нюанси.",
      topics: [
        { slug: "compiler-families", title: "GCC, Clang і MSVC: де вони розходяться", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "cross-compilation", title: "Крос-компіляція: хост, ціль і що між ними", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "target-triple-sysroot", title: "Цільовий тріплет і sysroot", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "build-flags", title: "Прапорці збірки: оптимізація, налагоджувальні символи, попередження", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "windows-toolchain-nuances", title: "Нюанси Windows: MSVC, рантайми, шляхи, кодування", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "android-ndk-nuances", title: "Нюанси Android: NDK, ABI, рівень API", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
  ]
});
