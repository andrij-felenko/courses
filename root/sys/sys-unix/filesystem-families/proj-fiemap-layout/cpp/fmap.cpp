// fmap.cpp — карта файлу на екстенти через FIEMAP (C++20).
#define _FILE_OFFSET_BITS 64

#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <array>
#include <memory>
#include <cstdint>
#include <cinttypes>
#include <cstdio>
#include <cstring>
#include <cerrno>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <linux/fiemap.h>
#include <linux/fs.h>

constexpr size_t SLOTS = 512;

struct FlagInfo {
    uint32_t bit;
    std::string_view name;
};

constexpr std::array FLAGNAME{
    FlagInfo{ FIEMAP_EXTENT_LAST,           "last"        },
    FlagInfo{ FIEMAP_EXTENT_UNKNOWN,        "unknown"     },
    FlagInfo{ FIEMAP_EXTENT_DELALLOC,       "delalloc"    },
    FlagInfo{ FIEMAP_EXTENT_ENCODED,        "encoded"     },
    FlagInfo{ FIEMAP_EXTENT_DATA_ENCRYPTED, "encrypted"   },
    FlagInfo{ FIEMAP_EXTENT_NOT_ALIGNED,    "not_aligned" },
    FlagInfo{ FIEMAP_EXTENT_DATA_INLINE,    "inline"      },
    FlagInfo{ FIEMAP_EXTENT_DATA_TAIL,      "tail"        },
    FlagInfo{ FIEMAP_EXTENT_UNWRITTEN,      "unwritten"   },
    FlagInfo{ FIEMAP_EXTENT_MERGED,         "merged"      },
    FlagInfo{ FIEMAP_EXTENT_SHARED,         "shared"      },
};

static std::string flags_str(uint32_t f)
{
    std::string out;
    for (const auto &item : FLAGNAME) {
        if (!(f & item.bit))
            continue;
        if (!out.empty())
            out += ',';
        out += item.name;
    }
    return out;
}
