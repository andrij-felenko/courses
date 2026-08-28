class SqlOrderDao implements OrderDao {
    private final DataSource ds;
    SqlOrderDao(DataSource ds) { this.ds = ds; }

    public List<OrderRow> findByStatus(String status) {
        String sql = "SELECT id, user_id, status, cents FROM orders "
                   + "WHERE status = ? ORDER BY id";
        try (Connection c = ds.getConnection();
             PreparedStatement st = c.prepareStatement(sql)) {
            st.setString(1, status);
            try (ResultSet rs = st.executeQuery()) {
                List<OrderRow> out = new ArrayList<>();
                while (rs.next())
                    out.add(new OrderRow(rs.getLong("id"), rs.getLong("user_id"),
                                         rs.getString("status"), rs.getLong("cents")));
                return out;
            }
        } catch (SQLException e) {
            throw new DataAccessException("findByStatus(" + status + ")", e);
        }
    }

    public void insert(OrderRow o) { /* INSERT ... як у SqlUserDao */ }
}
