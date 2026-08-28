/* Ідіоматична безпечна обробка через неволодіючий std::span у C++20 */
const auto* raw_payload = static_cast<const uint8_t*>(sqlite3_column_blob(stmt.get(), 2));
int payload_bytes = sqlite3_column_bytes(stmt.get(), 2);

std::span<const uint8_t> payload_view(raw_payload, static_cast<size_t>(payload_bytes));

if (payload_view.size() >= sizeof(uint32_t)) {
    uint32_t header = 0;
    std::memcpy(&header, payload_view.data(), sizeof(header));
    process_header(header);
}
