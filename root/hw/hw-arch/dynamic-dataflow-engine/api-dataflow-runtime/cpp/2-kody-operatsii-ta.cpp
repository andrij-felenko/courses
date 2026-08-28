#include <vector>

namespace dataflow {

enum class Opcode : uint8_t {
    Nop,
    Add,
    Sub,
    Mul,
    Div,
    Branch,
    Merge,
    IRead,
    IWrite,
    Call,
    Return
};

struct Arc {
    NodeId dest_node{0};
    Port   dest_port{0};
};

struct NodeDesc {
    Opcode           opcode{Opcode::Nop};
    bool             is_binary{false};
    uint8_t          slot_offset{0};
    std::vector<Arc> successors;
};

} // namespace dataflow
