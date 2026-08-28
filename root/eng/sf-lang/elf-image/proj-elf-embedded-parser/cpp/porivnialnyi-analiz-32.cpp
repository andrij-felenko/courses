#include <cstdint>
#include <span>
#include <concepts>

namespace elf {

struct Elf32Traits {
    using Address = std::uint32_t;
    using Offset  = std::uint32_t;
    using Word    = std::uint32_t;
};

struct Elf64Traits {
    using Address = std::uint64_t;
    using Offset  = std::uint64_t;
    using Word    = std::uint64_t;
};

template <typename Traits>
struct GenericProgramHeader {
    std::uint32_t type;
    std::uint32_t flags;
    typename Traits::Offset offset;
    typename Traits::Address vaddr;
    typename Traits::Address paddr;
    typename Traits::Word file_size;
    typename Traits::Word memory_size;
    typename Traits::Word align;
};

using ProgramHeader64 = GenericProgramHeader<Elf64Traits>;

} // namespace elf
