# Компіляція за стандартом C++11 із максимальним рівнем попереджень
g++ -std=c++11 -Wall -Wextra -Wpedantic main.cpp -o app_c11
clang++ -std=c++11 -Wall -Wextra -Wpedantic main.cpp -o app_c11

# Компіляція за стандартом C++14
g++ -std=c++14 -Wall -Wextra -Wpedantic main.cpp -o app_c14
clang++ -std=c++14 -Wall -Wextra -Wpedantic main.cpp -o app_c14

# Компілятор Microsoft Visual C++ (MSVC):
# Починаючи з VS 2015 Update 3 стандарт C++14 увімкнено за замовчуванням
cl.exe /std:c++14 /W4 /EHsc main.cpp /Fe:app_c14.exe
