// Прямий інлайнінг методів у C++20 (без виклику функцій через макроси або вказівники)
template <typename Graph, DFSVisitor Visitor>
void run_dfs_cpp_inlined(const Graph& g, Visitor& visitor, int u, 
                         std::vector<Color>& color, int& timer) {
    color[u] = Color::Gray;
    visitor.discover_vertex(u, ++timer);

    for (int v : g.neighbors(u)) {
        visitor.examine_edge(u, v);
        if (color[v] == Color::White) {
            visitor.tree_edge(u, v);
            run_dfs_cpp_inlined(g, visitor, v, color, timer);
            visitor.finish_edge(u, v);
        } else if (color[v] == Color::Gray) {
            visitor.back_edge(u, v);
        } else {
            visitor.forward_or_cross_edge(u, v);
        }
    }

    color[u] = Color::Black;
    visitor.finish_vertex(u, ++timer);
}
