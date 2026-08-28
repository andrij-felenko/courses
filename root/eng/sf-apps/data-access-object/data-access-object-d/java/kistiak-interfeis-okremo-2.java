// над реляційною базою: тут дозволено знати про SQL і драйвер
class SqlUserDao implements UserDao {
    private final DataSource ds;
    SqlUserDao(DataSource ds) { this.ds = ds; }

    public List<UserRow> findByRole(String role) {
        String sql = "SELECT id, email, role, active FROM users WHERE role = ?";
        try (Connection c = ds.getConnection();
             PreparedStatement st = c.prepareStatement(sql)) {
            st.setString(1, role);
            try (ResultSet rs = st.executeQuery()) {
                List<UserRow> out = new ArrayList<>();
                while (rs.next())
                    out.add(new UserRow(rs.getLong("id"), rs.getString("email"),
                                        rs.getString("role"), rs.getBoolean("active")));
                return out;
            }
        } catch (SQLException e) {
            throw new DataAccessException(e);   // перевинний виняток — не SQLException назовні
        }
    }
    // findById, insert, update, delete — так само над цим самим SQL
    // ...
}

// над звичайною мапою в пам'яті: жодної бази — для тестів
class InMemoryUserDao implements UserDao {
    private final Map<Long, UserRow> store = new HashMap<>();

    public List<UserRow> findByRole(String role) {
        return store.values().stream()
            .filter(u -> u.role().equals(role)).toList();
    }
    public void insert(UserRow u) { store.put(u.id(), u); }
    // findById, update, delete — над цією самою Map
    // ...
}
