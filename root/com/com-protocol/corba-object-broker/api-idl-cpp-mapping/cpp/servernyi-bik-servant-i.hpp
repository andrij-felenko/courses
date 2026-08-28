namespace PortableServer {
    class ServantBase {
    public:
        virtual ~ServantBase();
        virtual POA_ptr _default_POA();
        virtual Boolean _is_a(const char* logical_type_id);
        virtual Boolean _non_existent();
        virtual void    _add_ref();
        virtual void    _remove_ref();
        virtual ULong   _refcount_value();
    };
    typedef ServantBase* Servant;
}
