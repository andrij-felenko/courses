public Optional<UserRow> findById(long id) {
    String sql = "SELECT id, email, role, active FROM users WHERE id = ?";
    try (Connection c = ds.getConnection();                // 1) взяти з пулу
         PreparedStatement st = c.prepareStatement(sql)) {  // 2) підготувати
        st.setLong(1, id);
        try (ResultSet rs = st.executeQuery()) {            // 3) курсор
            return rs.next() ? Optional.of(map(rs)) : Optional.empty();
        }
    } catch (SQLException e) {
        throw new DataAccessException("findById(" + id + ")", e);
    }
    // усі три ресурси закриються в ЗВОРОТНОМУ порядку — навіть на винятку
}
