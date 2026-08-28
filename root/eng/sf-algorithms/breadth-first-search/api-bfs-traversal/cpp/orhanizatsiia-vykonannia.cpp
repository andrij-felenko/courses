#include <array>
#include <cstdint>
#include <cstddef>
#include <span >

template <std::size_t MaxV, typename Visitor>
void breadth_first_search_no_alloc(
    const std::vector<std::vector<int>>& adj,
    int start_node,
    std::array<std::uint32_t, (MaxV + 31) / 32>& visited_bits,
    std::array<int, MaxV>& queue_buf,
    Visitor visitor) 
{
    visited_bits.fill(0);
    auto set_bit = [&](int idx) { visited_bits[idx / 32] |= (1U << (idx % 32)); };
    auto get_bit = [&](int idx) { return (visited_bits[idx / 32] & (1U << (idx % 32))) != 0; };

    int head = 0, tail = 0;
    set_bit(start_node);
    visitor.discover_vertex(start_node);
    queue_buf[tail++] = start_node;

    while (head < tail) {
        int u = queue_buf[head++];
        visitor.examine_vertex(u);

        for (int v : adj[u]) {
            if (!get_bit(v)) {
                set_bit(v);
                visitor.tree_edge(v, u);
                queue_buf[tail++] = v;
            }
        }
    }
}
