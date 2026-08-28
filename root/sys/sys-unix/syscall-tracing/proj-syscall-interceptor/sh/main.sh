# 1. Компіляція ptrace трасувальника
gcc -std=c11 -O2 -Wall proj_ptrace.c -o ptrace_tracer_c
g++ -std=c++20 -O2 -Wall proj_ptrace.cpp -o ptrace_tracer_cpp

# 2. Компіляція Seccomp супервізора
gcc -std=c11 -O2 -Wall proj_seccomp.c -o seccomp_supervisor_c
g++ -std=c++20 -O2 -Wall proj_seccomp.cpp -o seccomp_supervisor_cpp

# 3. Тестування ptrace на системній утиліті ls
./ptrace_tracer_c /bin/ls /tmp

# 4. Тестування Seccomp супервізора
./seccomp_supervisor_c
ls -ld /tmp/virtual_c_dir
