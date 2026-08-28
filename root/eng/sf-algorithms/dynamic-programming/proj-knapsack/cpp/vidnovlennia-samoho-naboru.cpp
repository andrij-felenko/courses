vector<int> knap_items(const vector<vector<int>>& dp,
                       const vector<int>& wt, int cap) {
    int n = (int)wt.size(), w = cap;
    vector<int> taken;
    for (int i = n; i >= 1; --i)
        if (dp[i][w] != dp[i - 1][w]) {   // значення змінилося → річ i узято
            taken.push_back(i - 1);       // її індекс (від 0)
            w -= wt[i - 1];               // звільняємо зайняте нею місце
        }
    return taken;
}
