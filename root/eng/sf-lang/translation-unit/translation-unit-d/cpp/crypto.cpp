// crypto.cpp
namespace {
// У C++ анонімні простори імен є сучаснішою заміною static на рівні файлу.
// Вони надають внутрішнє зв'язування не лише функціям, а й класам та типам.
int g_private_seed = 42;

int internal_hash(int val) noexcept {
    return val ^ g_private_seed;
}
} // namespace

int public_encrypt(int raw) noexcept {
    return internal_hash(raw);
}
