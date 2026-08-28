#if defined(_MSC_VER)
    #define FORCE_INLINE [[msvc::forceinline]] inline
    #define PACKED_STRUCT_START __pragma(pack(push, 1))
    #define PACKED_STRUCT_END   __pragma(pack(pop))
#elif defined(__GNUC__) || defined(__clang__)
    #define FORCE_INLINE [[gnu::always_inline]] inline
    #define PACKED_STRUCT_START
    #define PACKED_STRUCT_END   __attribute__((packed))
#else
    #define FORCE_INLINE inline
    #define PACKED_STRUCT_START
    #define PACKED_STRUCT_END
#endif
