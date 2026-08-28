# Збірка версії C++:
$ g++ -std=c++23 -O2 elf_inspector.cpp -o elf_inspector

# Аудит системної утиліти curl:
$ ./elf_inspector /usr/bin/curl

=== ПАСПОРТ БІНАРНИКА ===
Клас:              ELF64
Порядок байтів:    Little-Endian (LSB)
Архітектура:       Advanced Micro Devices X86-64 (0x003e)
Тип файлу:         ET_DYN (Position-Independent Executable або Shared Object)
Точка входу:       0x000000000000b460

=== ЗАХИСНІ МЕХАНІЗМИ ТА ІНТЕРПРЕТАТОР ===
Тип зв'язування:   Динамічне (Dynamically linked)
Інтерпретатор:     /lib64/ld-linux-x86-64.so.2
NX (No-Execute):   Увімкнено (Стек захищено від виконання коду)
RELRO:             Присутній (PT_GNU_RELRO активний)
Символи:           stripped (Налагоджувальні символи видалено)

=== ДИНАМІЧНІ ЗАЛЕЖНОСТІ (DT_NEEDED) ===
  * Потрібна бібліотека: libcurl.so.4
  * Потрібна бібліотека: libc.so.6
  * Потрібна бібліотека: libz.so.1
