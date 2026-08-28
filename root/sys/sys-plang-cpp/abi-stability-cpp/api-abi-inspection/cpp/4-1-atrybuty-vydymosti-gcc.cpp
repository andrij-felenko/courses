#if defined(_WIN32) || defined(__CYGWIN__)
  #if defined(ENGINE_BUILDING_DLL)
    #define ENGINE_API __declspec(dllexport)
  #else
    #define ENGINE_API __declspec(dllimport)
  #endif
#else
  #if defined(__GNUC__) && __GNUC__ >= 4
    #define ENGINE_API __attribute__((visibility("default")))
    #define ENGINE_LOCAL __attribute__((visibility("hidden")))
  #else
    #define ENGINE_API
    #define ENGINE_LOCAL
  #endif
#endif

// Використання у публічних заголовках:
class ENGINE_API PublicEngine {
public:
    void start();  // Символ експортується у .dynsym
private:
    void step();   // Символ залишається локальним і прихованим
};
