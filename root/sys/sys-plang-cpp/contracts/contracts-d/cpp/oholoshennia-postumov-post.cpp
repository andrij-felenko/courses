int integer_square_root(int n) noexcept
    pre [positive_input]: n >= 0
    post(result): result >= 0 && (result * result <= n) && ((result + 1) * (result + 1) > n)
{
    int r = 0;
    while ((r + 1) * (r + 1) <= n) {
        ++r;
    }
    return r;
}
