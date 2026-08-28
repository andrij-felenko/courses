char* names[] = { "Петренко", "Коваль" };

// ✗ — сервант вважає, що прапорець TRUE, і спробує звільнити літерали
bank::NameSeq seq(2, 2, names, FALSE);
svc->rename(seq);

// ✓ — послідовність володіє власними рядками
bank::NameSeq seq(2);
seq.length(2);
seq[0] = CORBA::string_dup("Петренко");
seq[1] = CORBA::string_dup("Коваль");
svc->rename(seq);
