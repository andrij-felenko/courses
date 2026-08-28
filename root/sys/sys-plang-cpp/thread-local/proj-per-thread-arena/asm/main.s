; Вхідні параметри: %rdi = this (покажчик на арену), %rsi = bytes (розмір)
allocate_hot_path:
    movq    8(%rdi), %rax          ; %rax = offset_ (зміщення)
    movq    (%rdi), %rdx           ; %rdx = buffer_ (базова адреса буфера)
    leaq    63(%rax,%rsi), %rcx    ; %rcx = offset_ + bytes + 63
    andq    $-64, %rcx             ; %rcx = вирівнювання за 64 байтами (нова адреса)
    cmpq    16(%rdi), %rcx         ; Порівняння: new_offset <= capacity_ ?
    ja      .Lgrow_slow_path       ; Якщо вичерпано -> перехід на повільний шлях grow()
    movq    %rcx, 8(%rdi)          ; offset_ = new_offset (збереження стану)
    addq    %rdx, %rax             ; Повертаний покажчик = buffer_ + old_offset
    retq                           ; Повернення з функції
.Lgrow_slow_path:
    jmp     ThreadLocalArena::grow ; Рідкісний виклик аллокації нового блоку
