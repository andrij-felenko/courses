#include <functional>

namespace driver {

struct TransferResult {
    Status status;
    size_t bytes_transferred;
};

/* C++20 варіант: статичний функціональний об'єкт або покажчик на вільну функцію */
using DriverCallback = void (*)(I2cDriver& driver, TransferResult result, void* user_data);

} // namespace driver
