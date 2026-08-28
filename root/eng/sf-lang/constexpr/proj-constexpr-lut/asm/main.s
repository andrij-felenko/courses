calculate_stream(std::string_view):
    mov     rax, rsi                ; rax = розмір рядка (довжина)
    test    rsi, rsi
    je      .Lempty                 ; Якщо буфер порожній — повернути 0
    mov     edx, -1                 ; edx = crc (0xFFFFFFFF)
    xor     ecx, ecx                ; ecx = індекс ітератора
.Lloop:
    movzx   esi, byte ptr [rdi+rcx] ; esi = читання чергового байта з буфера
    xor     esi, edx                ; esi = crc ^ byte
    movzx   esi, sil                ; esi = молодший байт (індекс у таблиці)
    shr     edx, 8                  ; edx = crc >> 8
    xor     edx, dword ptr [crc32::TABLE+rsi*4] ; edx ^= TABLE[index]
    inc     rcx
    cmp     rax, rcx
    jne     .Lloop                  ; Перехід на наступну ітерацію циклу
    not     edx                     ; edx = crc ^ 0xFFFFFFFF
    mov     eax, edx
    ret
.Lempty:
    xor     eax, eax
    ret
