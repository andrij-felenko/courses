benchmark_access(InPlaceOptional<ImmutableConfig>&):
    ; Перший emplace: запис 8080 та 100 у сховище
    mov    dword ptr [rdi], 8080
    mov    dword ptr [rdi + 4], 100
    mov    byte ptr [rdi + 8], 1      ; engaged_ = true

    ; Другий emplace: запис 9090 та 200 у те саме сховище
    mov    dword ptr [rdi], 9090
    mov    dword ptr [rdi + 4], 200

    ; ОБЧИСЛЕННЯ РЕЗУЛЬТАТУ:
    ; Оптимізатор порахував: p1 = 8080.
    ; Для p2 він вирішив: поле port константне, отже p2 теж дорівнює 8080!
    ; Результат: 8080 + 8080 = 16160 замість (8080 + 9090 = 17170)
    mov    eax, 16160
    ret
