/* Потоконебезпечний генератор ідентифікаторів */
namespace unsafe_generator {

static unsigned long g_next_id = 1;

unsigned long generate_id() noexcept {
    return g_next_id++;
}

} // namespace unsafe_generator
