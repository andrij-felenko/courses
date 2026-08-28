// C++ оголошення інтерфейсу getopt_long у системному просторі
#include <cstddef>
#include <getopt.h>

namespace posix_cli {
    using OptionStruct = ::option;
    
    inline int parse_options(int argc, char *const argv[],
                             const char *optstring,
                             const OptionStruct *longopts,
                             int *longindex) noexcept {
        return ::getopt_long(argc, argv, optstring, longopts, longindex);
    }
}
