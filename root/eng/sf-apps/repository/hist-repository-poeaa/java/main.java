// типовий DAO зразка 2001-го: один клас на таблицю,
// імена методів — з лексикону бази, назовні — плоскі записи
public class OrderDAO {
    private final DataSource ds;

    public OrderDAO(DataSource ds) { this.ds = ds; }

    public void insert(OrderVO order) throws SQLException {
        Connection c = ds.getConnection();
        try {
            PreparedStatement ps = c.prepareStatement(
                "INSERT INTO orders (id, customer_id, total, status) VALUES (?, ?, ?, ?)");
            ps.setString(1, order.getId());
            ps.setString(2, order.getCustomerId());
            ps.setBigDecimal(3, order.getTotal());
            ps.setString(4, order.getStatus());
            ps.executeUpdate();
        } finally {
            c.close();
        }
    }

    public List findByStatus(String status) throws SQLException {
        Connection c = ds.getConnection();
        try {
            PreparedStatement ps = c.prepareStatement(
                "SELECT id, customer_id, total, status FROM orders WHERE status = ?");
            ps.setString(1, status);
            ResultSet rs = ps.executeQuery();
            List result = new ArrayList();   // дженериків у Java 2001-го ще нема
            while (rs.next()) {
                OrderVO vo = new OrderVO();
                vo.setId(rs.getString("id"));
                vo.setCustomerId(rs.getString("customer_id"));
                vo.setTotal(rs.getBigDecimal("total"));
                vo.setStatus(rs.getString("status"));
                result.add(vo);              // плоский носій колонок, без поведінки
            }
            return result;
        } finally {
            c.close();
        }
    }

    // ще update(OrderVO) і delete(String) — механіка та сама
}
