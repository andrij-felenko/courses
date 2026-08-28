int main() {
    // Будь-яка комбінація збирається на місці — БЕЗ нового типу.
    Enemy knight(std::make_unique<Sword>(), std::make_unique<Heavy>());
    Enemy archer(std::make_unique<Bow>(),   std::make_unique<Light>());
    Enemy mage  (std::make_unique<Sword>(), std::make_unique<Magic>());

    knight.describe();   // ворог: меч + важка → атака 10, захист 7
    archer.describe();   // ворог: лук + легка → атака 6,  захист 2
    mage.describe();     // ворог: меч + магічна → атака 10, захист 5
    return 0;
}
