class SqlUserDao implements UserDao {
    private final DataSource ds;
    SqlUserDao(DataSource ds) { this.ds = ds; }

    public List<UserRow> findByRole(String role) {
        String sql = "SELECT id, email, role, active FROM users "
                   + "WHERE role = ? ORDER BY id";
        try (Connection c = ds.getConnection();
             PreparedStatement st = c.prepareStatement(sql)) {
            st.setString(1, role);                       // параметр, а не склейка рядка
            try (ResultSet rs = st.executeQuery()) {
                List<UserRow> out = new ArrayList<>();
                while (rs.next()) out.add(map(rs));
                return out;
            }
        } catch (SQLException e) {
            throw new DataAccessException("findByRole(" + role + ")", e);
        }
    }

    public List<UserRow> findByIds(Collection<Long> ids) {
        if (ids.isEmpty()) return List.of();             // порожній список — не ходити в базу
        String marks = ids.stream().map(x -> "?").collect(joining(", "));
        String sql = "SELECT id, email, role, active FROM users "
                   + "WHERE id IN (" + marks + ") ORDER BY id";
        try (Connection c = ds.getConnection();
             PreparedStatement st = c.prepareStatement(sql)) {
            int i = 1;
            for (Long id : ids) st.setLong(i++, id);
            try (ResultSet rs = st.executeQuery()) {
                List<UserRow> out = new ArrayList<>();
                while (rs.next()) out.add(map(rs));
                return out;
            }
        } catch (SQLException e) {
            throw new DataAccessException("findByIds", e);
        }
    }

    public void insert(UserRow u) {
        String sql = "INSERT INTO users(id, email, role, active) VALUES (?, ?, ?, ?)";
        try (Connection c = ds.getConnection();
             PreparedStatement st = c.prepareStatement(sql)) {
            st.setLong(1, u.id());
            st.setString(2, u.email());
            st.setString(3, u.role());
            st.setBoolean(4, u.active());
            st.executeUpdate();
        } catch (SQLException e) {
            throw new DataAccessException("insert(" + u.id() + ")", e);
        }
    }

    // findById, update, delete — так само над цим самим SQL
    // ...

    private static UserRow map(ResultSet rs) throws SQLException {
        return new UserRow(rs.getLong("id"), rs.getString("email"),
                           rs.getString("role"), rs.getBoolean("active"));
    }
}
