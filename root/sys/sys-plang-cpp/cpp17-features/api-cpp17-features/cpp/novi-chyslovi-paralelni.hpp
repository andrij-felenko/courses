#include <numeric>
#include <execution>
#include <vector>

std::vector<double> values(10'000'000, 1.5);

// std::reduce: паралельне підсумовування (вимагає асоціативності та комутативності)
double sum = std::reduce(std::execution::par, values.begin(), values.end(), 0.0);

// std::transform_reduce: паралельний MapReduce
std::vector<double> weights(10'000'000, 2.0);
double dot_product = std::transform_reduce(
    std::execution::par_unseq,
    values.begin(), values.end(),
    weights.begin(),
    0.0,
    std::plus<>(),        // Reducer
    std::multiplies<>()   // Transformer
);

// Префіксні суми
std::vector<double> inclusive_out(values.size());
std::inclusive_scan(std::execution::par, values.begin(), values.end(), inclusive_out.begin());

std::vector<double> exclusive_out(values.size());
std::exclusive_scan(std::execution::par, values.begin(), values.end(), exclusive_out.begin(), 0.0);
