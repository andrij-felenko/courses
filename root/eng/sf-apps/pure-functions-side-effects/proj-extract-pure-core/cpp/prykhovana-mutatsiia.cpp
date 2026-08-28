struct Cart {
    std::vector<Item>* items;   // ПОКАЖЧИК: const його не захистить
    Discount*          policy;
};

double computeBad(const Cart& cart) {   // cart const, але...
    cart.items->push_back({0,0});       // ← змінюємо чужі дані! компілюється!
    cart.policy->timesUsed++;           // ← і ще раз! теж компілюється
    // ...
}
