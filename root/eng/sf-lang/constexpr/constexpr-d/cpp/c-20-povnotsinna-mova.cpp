   #include <vector>
   #include <numeric>
   #include <algorithm>

   constexpr int sum_of_sorted_evens() {
       std::vector<int> data = {9, 2, 7, 4, 5, 6, 1, 8};
       data.erase(std::remove_if(data.begin(), data.end(), [](int x) { return x % 2 != 0; }), data.end());
       std::sort(data.begin(), data.end());
       
       int sum = std::accumulate(data.begin(), data.end(), 0);
       return sum; // Вектор data знищується тут, пам'ять звільняється через delete
   }

   static_assert(sum_of_sorted_evens() == 20); // Працює на етапі компіляції!
