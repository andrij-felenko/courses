    void push(long long key, int id) {          // O(log n)
        h.push_back({key, id});
        pos[id] = (int)h.size() - 1;            // новачок — у кінці
        sift_up((int)h.size() - 1);
    }

    void sift_up(int i) {
        while (i > 0) {
            int parent = (i - 1) / 2;
            if (h[parent].key <= h[i].key) break;   // батько вже менший — стоп
            swap_nodes(i, parent);
            i = parent;
        }
    }
