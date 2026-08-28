int main() {
    ORSet A(1), B(2);        // дві репліки з різними id

    A.add("x");              // A карбує тег {1,1} для x
    B.merge(A);              // B дізнається про x через тег {1,1}; тепер обидві згодні

    // --- мережа рветься; A і B діють ОДНОЧАСНО ---
    A.remove("x");           // A надгробить бачений тег x: {1,1}
    B.add("x");              // B карбує СВІЖИЙ тег {2,1} для x

    // Зливаємо два розбіжні стани — пробуємо ОБИДВА порядки:
    ORSet ab = A; ab.merge(B);   // (видалив) а потім (додав)
    ORSet ba = B; ba.merge(A);   // (додав) а потім (видалив)

    std::cout << "A|B contains x: " << ab.contains("x") << "\n";   // 1 — додавання перемогло
    std::cout << "B|A contains x: " << ba.contains("x") << "\n";   // 1 — та сама відповідь
    std::cout << "identical: "
              << (ab.addTags == ba.addTags && ab.tombstones == ba.tombstones) << "\n";  // 1
}
