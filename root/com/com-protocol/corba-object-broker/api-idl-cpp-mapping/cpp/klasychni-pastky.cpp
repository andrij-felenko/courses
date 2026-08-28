// ✗ — якщо audit() кине, послідовність загублено
bank::StatementSeq* Account_i::history() {
    bank::StatementSeq* out = new bank::StatementSeq(n);
    fill(*out);
    audit("history");
    return out;
}

// ✓ — власність тримає _var, а _retn() віддає її рівно на виході
bank::StatementSeq* Account_i::history() {
    bank::StatementSeq_var out = new bank::StatementSeq(n);
    fill(*out);
    audit("history");
    return out._retn();
}
