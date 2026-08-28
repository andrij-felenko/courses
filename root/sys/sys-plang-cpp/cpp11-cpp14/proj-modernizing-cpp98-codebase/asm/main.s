; Асемблерний лістинг переміщення std::vector на x86-64 (System V ABI)
; rsi вказує на вихідний об'єкт large_payload
; rdi вказує на внутрішнє поле buffer у згенерованій структурі лямбди

mov   rax, qword ptr [rsi]        ; rax = large_payload.data_ptr
mov   rcx, qword ptr [rsi + 8]    ; rcx = large_payload.size_ptr
mov   rdx, qword ptr [rsi + 16]   ; rdx = large_payload.capacity_ptr

mov   qword ptr [rdi], rax        ; buffer.data_ptr = rax
mov   qword ptr [rdi + 8], rcx    ; buffer.size_ptr = rcx
mov   qword ptr [rdi + 16], rdx   ; buffer.capacity_ptr = rdx

mov   qword ptr [rsi], 0          ; large_payload.data_ptr = nullptr
mov   qword ptr [rsi + 8], 0      ; large_payload.size_ptr = nullptr
mov   qword ptr [rsi + 16], 0     ; large_payload.capacity_ptr = nullptr
