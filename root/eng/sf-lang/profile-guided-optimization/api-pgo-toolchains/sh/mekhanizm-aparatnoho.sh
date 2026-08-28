# Крок 1. Компіляція з налагоджувальними мітками (без зміни коду програми)
clang++ -O3 -gline-tables-only -fdebug-info-for-profiling main.cpp -o app_server

# Крок 2. Збір траси переходів через perf LBR на бойовому сервері (тривалість 60 с)
perf record -b -e br_inst_retired.near_taken:pp -c 1000003 -o perf.data -- ./app_server

# Крок 3. Перетворення траси апаратних адрес у формат вихідних рядків LLVM
create_llvm_prof --binary=app_server --profile=perf.data --out=app.afdo

# Крок 4. Компіляція релізу з використанням вибіркового профілю
clang++ -O3 -fprofile-sample-use=app.afdo main.cpp -o app_server_opt
