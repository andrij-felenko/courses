#include <contracts>
#include <cmath>
#include <span>

// Функція обчислення середнього значення вибірки з повним контрактним захистом
double compute_sample_mean(std::span<const double> data)
    pre (!data.empty())                             // Преумова: вибірка не може бути порожньою
    post [mean] (!std::isnan(mean) && mean >= 0.0) // Постумова: середнє повинно бути валідним числом
{
    double sum = 0.0;
    for (double val : data) {
        contract_assert(val >= 0.0); // Внутрішній інваріант: відсутність від'ємних значень у сенсорі
        sum += val;
    }
    return sum / static_cast<double>(data.size());
}
