namespace CORBA {
    void    release(Object_ptr obj);   // на порожньому посиланні — нічого не робить
    Boolean is_nil(Object_ptr obj);    // єдиний законний спосіб перевірити на порожнечу
}
// жодна з цих двох не кидає винятків

class bank::Account {
public:
    static Account_ptr _duplicate(Account_ptr obj);      // може кинути системний виняток
    static Account_ptr _narrow(CORBA::Object_ptr obj);   // може кинути системний виняток
    static Account_ptr _nil();                           // не кидає нічого
};
