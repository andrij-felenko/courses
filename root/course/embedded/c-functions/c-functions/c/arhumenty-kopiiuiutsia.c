void try_to_change(int x) {
    x = 100;              // міняємо копію всередині функції
}

int main() {
    int n = 5;
    try_to_change(n);    // передали копію 5
    printf("%d\n", n);   // надрукує 5, а не 100!
    return 0;
}
