auto root = std::make_unique<Group>();

auto innerOwned = std::make_unique<Group>();
Group* inner = innerOwned.get();                 // тримаємо не-власний доступ, поки не віддали володіння
root->add(std::move(innerOwned));

auto r1Owned = std::make_unique<Rectangle>(0, 0, 10, 10);
Rectangle* r1 = r1Owned.get();
inner->add(std::move(r1Owned));
inner->add(std::make_unique<Rectangle>(20, 0, 10, 10));
root->add(std::make_unique<Rectangle>(100, 100, 5, 5));

root->bounds();        // ПЕРШИЙ запит: повний перерахунок → {0,0,105,105}
root->bounds();        // усе чисте → O(1)
r1->moveTo(-50, -50);  // листок поїхав → inner і root брудні
root->bounds();        // перерахунок лише брудного шляху → {-50,-50,105,105}
