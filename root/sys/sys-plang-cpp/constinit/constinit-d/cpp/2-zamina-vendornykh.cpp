// Було: вендорні макроси
#if defined(__clang__)
#define REQUIRE_CONST_INIT [[clang::require_constant_initialization]]
#elif defined(__GNUC__)
#define REQUIRE_CONST_INIT __attribute__((require_constant_initialization))
#else
#define REQUIRE_CONST_INIT
#endif

REQUIRE_CONST_INIT static Mutex g_mutex;

// Стало: чистий стандартизований C++20
constinit static Mutex g_mutex;
