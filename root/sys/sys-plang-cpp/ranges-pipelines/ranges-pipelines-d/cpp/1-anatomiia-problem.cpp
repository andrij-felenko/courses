// Класичний жадібний підхід STL (C++11):
std::vector<Record> raw_data = read_telemetry();

// Етап 1: Витягування кодів (створюється перший тимчасовий вектор)
std::vector<int> codes;
codes.reserve(raw_data.size());
std::transform(raw_data.begin(), raw_data.end(), std::back_inserter(codes),
               [](const Record& r) { return r.code; });

// Етап 2: Фільтрація (створюється другий тимчасовий вектор)
std::vector<int> filtered_codes;
std::copy_if(codes.begin(), codes.end(), std::back_inserter(filtered_codes),
             [](int code) { return code > 400; });

// Етап 3: Трансформація (створюється третій тимчасовий вектор)
std::vector<double> scaled_values;
scaled_values.reserve(filtered_codes.size());
std::transform(filtered_codes.begin(), filtered_codes.end(), std::back_inserter(scaled_values),
               [](int code) { return code * 1.5; });

// Етап 4: Обрізання до K елементів (четвертий вектор)
std::vector<double> final_result(scaled_values.begin(), 
                                 scaled_values.begin() + std::min<size_t>(10, scaled_values.size()));
