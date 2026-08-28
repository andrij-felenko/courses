// Традиційний марудно написаний компаратор
bool compare_manual(const CityRecord& a, const CityRecord& b) {
    if (a.country != b.country) return a.country < b.country;
    if (a.city != b.city) return a.city < b.city;
    return a.population < b.population;
}

// Ідіоматичний та елегантний C++ компаратор через std::tie
bool compare_tuple(const CityRecord& a, const CityRecord& b) {
    return std::tie(a.country, a.city, a.population) <
           std::tie(b.country, b.city, b.population);
}
