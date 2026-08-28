#pragma once

#if defined(_WIN32) || defined(__CYGWIN__)
  #if defined(HYPERION_STATIC_DEFINE)
    #define HYPERION_API
  #elif defined(hyperion_core_EXPORTS)
    #define HYPERION_API __declspec(dllexport)
  #else
    #define HYPERION_API __declspec(dllimport)
  #endif
#else
  #if defined(__GNUC__) && __GNUC__ >= 4
    #define HYPERION_API __attribute__((visibility("default")))
  #else
    #define HYPERION_API
  #endif
#endif
