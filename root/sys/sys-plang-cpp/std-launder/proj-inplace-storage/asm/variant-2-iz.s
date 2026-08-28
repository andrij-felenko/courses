benchmark_access(InPlaceOptional<ImmutableConfig>&):
    ; Перший emplace
    mov    dword ptr [rdi], 8080
    mov    dword ptr [rdi + 4], 100
    mov    byte ptr [rdi + 8], 1

    ; Другий emplace
    mov    dword ptr [rdi], 9090
    mov    dword ptr [rdi + 4], 200

    ; ОБЧИСЛЕННЯ РЕЗУЛЬТАТУ:
    ; Завдяки std::launder оптимізатор завантажує актуальне значення port з пам'яті:
    mov    eax, dword ptr [rdi]       ; чесне завантаження 9090
    add    eax, 8080                  ; 8080 + 9090 = 17170
    ret
