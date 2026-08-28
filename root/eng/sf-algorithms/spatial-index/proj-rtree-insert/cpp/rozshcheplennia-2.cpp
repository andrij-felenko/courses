static Node* quadraticSplit(Node* n) {
    std::vector<Entry> all;
    all.swap(n->e);                        // забираємо всі M+1 записів

    int s1, s2;
    pickSeeds(all, s1, s2);

    Node* nn = new Node(n->leaf);
    n->e.push_back(all[s1]);   Rect b1 = all[s1].box;
    nn->e.push_back(all[s2]);  Rect b2 = all[s2].box;

    std::vector<char> used(all.size(), 0);
    used[s1] = used[s2] = 1;
    size_t left = all.size() - 2;

    while (left > 0) {
        // групі бракує записів до m — віддаємо їй усе, що лишилось
        if (n->e.size() + left == (size_t)m || nn->e.size() + left == (size_t)m) {
            bool toFirst = (n->e.size() + left == (size_t)m);
            for (size_t i = 0; i < all.size(); ++i) if (!used[i]) {
                if (toFirst) { n->e.push_back(all[i]);  b1 = unite(b1, all[i].box); }
                else         { nn->e.push_back(all[i]); b2 = unite(b2, all[i].box); }
            }
            break;
        }
        // pickNext: запис із найвиразнішою перевагою
        int pick = -1; double bestDiff = -1.0;
        for (size_t i = 0; i < all.size(); ++i) {
            if (used[i]) continue;
            double diff = std::fabs(enlargement(b1, all[i].box)
                                  - enlargement(b2, all[i].box));
            if (diff > bestDiff) { bestDiff = diff; pick = (int)i; }
        }
        double d1 = enlargement(b1, all[pick].box);
        double d2 = enlargement(b2, all[pick].box);
        bool toFirst = (d1 != d2)                 ? (d1 < d2)
                     : (area(b1) != area(b2))     ? (area(b1) < area(b2))
                                                  : (n->e.size() <= nn->e.size());
        if (toFirst) { n->e.push_back(all[pick]);  b1 = unite(b1, all[pick].box); }
        else         { nn->e.push_back(all[pick]); b2 = unite(b2, all[pick].box); }
        used[pick] = 1;
        --left;
    }
    if (!n->leaf)                              // дітям, що переїхали, — новий батько
        for (Entry& en : nn->e) en.child->parent = nn;
    return nn;
}
