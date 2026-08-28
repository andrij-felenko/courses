struct Config {
    const std::string name;   // виглядає «правильно»
    int retries;
};

std::vector<Config> v;
v.push_back({"a", 3});                        // ✓ конструюванням — можна
std::sort(v.begin(), v.end(), by_retries);    // ✗ sort присвоює елементи
v.erase(v.begin());                           // ✗ erase зсуває хвіст присвоєнням
std::swap(v[0], v[1]);                        // ✗ swap — це три присвоєння
