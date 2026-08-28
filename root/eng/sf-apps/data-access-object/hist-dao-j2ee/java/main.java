// абстрактна фабрика: приховує, з якого сховища беруться DAO
abstract class DAOFactory {
    abstract OrderDAO    getOrderDAO();
    abstract CustomerDAO getCustomerDAO();

    static DAOFactory getFactory(int whichStore) {   // RDB, LDAP, …
        switch (whichStore) {
            case RDB:  return new RdbDAOFactory();
            case LDAP: return new LdapDAOFactory();
            default:   return null;
        }
    }
}

// конкретна фабрика під реляційну базу
class RdbDAOFactory extends DAOFactory {
    OrderDAO    getOrderDAO()    { return new RdbOrderDAO(); }
    CustomerDAO getCustomerDAO() { return new RdbCustomerDAO(); }
}
