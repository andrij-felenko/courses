struct CommonBase {
    virtual void base_fn();
    int32_t base_id; // 4 байти
};

struct InterfaceA : virtual public CommonBase {
    virtual void fn_a();
    int32_t a_val;   // 4 байти
};

struct InterfaceB : virtual public CommonBase {
    virtual void fn_b();
    int32_t b_val;   // 4 байти
};

struct ConcreteCombined : public InterfaceA, public InterfaceB {
    int64_t combined_id; // 8 байтів
};
