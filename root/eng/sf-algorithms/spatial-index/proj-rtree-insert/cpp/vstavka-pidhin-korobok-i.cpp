struct Tree {
    Node* root;
    Tree() : root(new Node(true)) {}

    void insert(const Rect& box, int id) {
        Node* n = root;
        while (!n->leaf) n = n->e[chooseSubtree(n, box)].child;
        n->e.push_back(Entry{ box, nullptr, id });
        Node* split = (n->e.size() > (size_t)M) ? quadraticSplit(n) : nullptr;
        adjustTree(n, split);
    }

    void adjustTree(Node* n, Node* nn) {
        while (n != root) {
            Node* p = n->parent;
            for (Entry& en : p->e)
                if (en.child == n) { en.box = cover(n); break; }
            if (nn) {
                nn->parent = p;
                p->e.push_back(Entry{ cover(nn), nn, -1 });
                nn = (p->e.size() > (size_t)M) ? quadraticSplit(p) : nullptr;
            }
            n = p;
        }
        if (nn) {                                  // розщепився корінь
            Node* r = new Node(false);
            root->parent = r; nn->parent = r;
            r->e.push_back(Entry{ cover(root), root, -1 });
            r->e.push_back(Entry{ cover(nn),   nn,   -1 });
            root = r;
        }
    }

    void query(const Rect& w, std::vector<int>& out) const { search(root, w, out); }

    static void search(const Node* n, const Rect& w, std::vector<int>& out) {
        for (const Entry& en : n->e) {
            if (!intersects(en.box, w)) continue;  // ← усе відсікання дерева тут
            if (n->leaf) out.push_back(en.id);
            else search(en.child, w, out);
        }
    }
};
