static void pickSeeds(const std::vector<Entry>& all, int& s1, int& s2) {
    double worst = -std::numeric_limits<double>::infinity();
    s1 = 0; s2 = 1;
    for (size_t i = 0; i < all.size(); ++i)
        for (size_t j = i + 1; j < all.size(); ++j) {
            double d = area(unite(all[i].box, all[j].box))
                     - area(all[i].box) - area(all[j].box);
            if (d > worst) { worst = d; s1 = (int)i; s2 = (int)j; }
        }
}
