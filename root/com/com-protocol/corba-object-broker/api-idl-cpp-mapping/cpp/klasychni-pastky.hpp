// IDL: void last_statement(out string s);

// ✗ — десять рядків, жоден не звільнено
char* s;
for (int i = 0; i < 10; ++i)
    acc->last_statement(s);

// ✓ — out() звільняє попереднє значення сам
CORBA::String_var s;
for (int i = 0; i < 10; ++i)
    acc->last_statement(s);
