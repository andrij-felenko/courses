// ==================== Ламання vtable у C++ ====================
// ВЕРСІЯ 1
class Widget {
public:
    virtual void draw();   // vtable[0]
    virtual void resize(); // vtable[1]
};

// ВЕРСІЯ 2 (ЗЛАМАНО ABI!)
class Widget {
public:
    virtual void audit();  // vtable[0] — НОВИЙ МЕТОД ЗМІСТИВ ІНДЕКСИ!
    virtual void draw();   // vtable[1] (старий код викликає тут audit!)
    virtual void resize(); // vtable[2]
};
