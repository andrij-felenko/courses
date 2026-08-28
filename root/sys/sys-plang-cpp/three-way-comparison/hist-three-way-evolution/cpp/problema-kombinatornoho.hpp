// 1. Порівняння двох об'єктів MyString (6 операторів)
bool operator==(const MyString&, const MyString&);
bool operator!=(const MyString&, const MyString&);
bool operator< (const MyString&, const MyString&);
bool operator<=(const MyString&, const MyString&);
bool operator> (const MyString&, const MyString&);
bool operator>=(const MyString&, const MyString&);

// 2. Порівняння MyString з const char* (6 операторів)
bool operator==(const MyString&, const char*);
bool operator!=(const MyString&, const char*);
bool operator< (const MyString&, const char*);
bool operator<=(const MyString&, const char*);
bool operator> (const MyString&, const char*);
bool operator>=(const MyString&, const char*);

// 3. Зворотне порівняння const char* з MyString (ще 6 операторів!)
bool operator==(const char*, const MyString&);
bool operator!=(const char*, const MyString&);
bool operator< (const char*, const MyString&);
bool operator<=(const char*, const MyString&);
bool operator> (const char*, const MyString&);
bool operator>=(const char*, const MyString&);
