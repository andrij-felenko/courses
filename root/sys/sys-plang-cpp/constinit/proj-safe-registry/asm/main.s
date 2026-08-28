; Звернення до Meyers' Singleton get_registry():
movzbl  guard_variable_for_get_registry(%rip), %eax ; Перевірка байта захисту
testb   %al, %al
jne     .L_already_inited                           ; Швидкий перехід, якщо вже ініціалізовано
leaq    guard_variable_for_get_registry(%rip), %rdi
call    __cxa_guard_acquire                         ; Системний виклик блокування
testl   %eax, %eax
je      .L_already_inited
...
call    __cxa_guard_release                         ; Звільнення блокування
.L_already_inited:
movq    instance_memory(%rip), %rax
