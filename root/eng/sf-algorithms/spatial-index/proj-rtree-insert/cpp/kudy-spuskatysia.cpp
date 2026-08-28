static int chooseSubtree(const Node* n, const Rect& add) {
    int best = 0;
    double bestEnl = std::numeric_limits<double>::infinity();
    double bestArea = std::numeric_limits<double>::infinity();
    for (size_t i = 0; i < n->e.size(); ++i) {
        double enl = enlargement(n->e[i].box, add);
        double ar  = area(n->e[i].box);
        if (enl < bestEnl || (enl == bestEnl && ar < bestArea)) {
            best = (int)i; bestEnl = enl; bestArea = ar;
        }
    }
    return best;
}
