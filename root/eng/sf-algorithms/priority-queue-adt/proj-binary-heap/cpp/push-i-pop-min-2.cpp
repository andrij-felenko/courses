    Node pop_min() {                             // O(log n)
        swap_nodes(0, (int)h.size() - 1);       // корінь -> у хвіст
        Node top = h.back();
        h.pop_back();                           // і геть із масиву
        pos[top.id] = NONE;                     // елемент вийшов із черги
        if (!h.empty()) sift_down(0);
        return top;
    }

    void sift_down(int i) {
        int n = (int)h.size();
        for (;;) {
            int smallest = i, l = 2*i + 1, r = 2*i + 2;
            if (l < n && h[l].key < h[smallest].key) smallest = l;   // менша дитина
            if (r < n && h[r].key < h[smallest].key) smallest = r;
            if (smallest == i) break;           // обидві діти більші — на місці
            swap_nodes(i, smallest);
            i = smallest;
        }
    }
