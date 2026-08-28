List<String> approverEmails() {
    List<String> emails = new ArrayList<>();
    Connection conn = null;
    try {
        conn = pool.getConnection();
        PreparedStatement st = conn.prepareStatement(
            "SELECT email FROM users WHERE role = ? AND active = 1");
        st.setString(1, "approver");
        ResultSet rs = st.executeQuery();
        while (rs.next()) {
            emails.add(rs.getString("email"));   // єдиний змістовний рядок
        }
        return emails;
    } catch (SQLException e) {
        throw new RuntimeException(e);
    } finally {
        if (conn != null) try { conn.close(); } catch (SQLException ignore) {}
    }
}
