/* prod[0..2n) = a[0..n)²  — множення «стовпчиком», O(n²) */
static void square(const limb *a, int n, limb *prod) {
    memset(prod, 0, 2 * n * sizeof(limb));
    for (int i = 0; i < n; i++) {
        uint64_t carry = 0;
        for (int j = 0; j < n; j++) {
            uint64_t cur = (uint64_t)prod[i + j] + (uint64_t)a[i] * a[j] + carry;
            prod[i + j] = (limb)cur;
            carry = cur >> 32;
        }
        prod[i + n] += (limb)carry;
    }
}
