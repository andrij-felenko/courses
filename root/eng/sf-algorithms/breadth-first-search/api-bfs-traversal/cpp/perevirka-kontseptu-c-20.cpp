#include <concepts>

template <typename V>
concept BFSVisitorConcept = requires(V& visitor, int u, int v) {
    { visitor.initialize_vertex(u) } -> std::same_as<void>;
    { visitor.start_vertex(u) }      -> std::same_as<void>;
    { visitor.discover_vertex(u) }   -> std::same_as<void>;
    { visitor.examine_vertex(u) }    -> std::same_as<void>;
    { visitor.examine_edge(u, v) }   -> std::same_as<void>;
    { visitor.tree_edge(u, v) }      -> std::same_as<void>;
    { visitor.non_tree_edge(u, v) }  -> std::same_as<void>;
    { visitor.finish_vertex(u) }     -> std::same_as<void>;
};
