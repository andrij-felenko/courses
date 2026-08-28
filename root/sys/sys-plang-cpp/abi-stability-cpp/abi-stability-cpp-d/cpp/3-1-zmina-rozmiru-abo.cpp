// v1.0 у shared library
class Session {
public:
    int get_id() const { return id_; }
private:
    int id_;         // зміщення +0
    double timeout_; // зміщення +8
};

// v1.1: Розробник додав нове приватне поле
class Session {
public:
    int get_id() const { return id_; }
private:
    int id_;             // зміщення +0
    bool authenticated_; // зміщення +4 (НОВЕ ПОЛЕ)
    double timeout_;     // зміщення +8 -> зсунулося на +16 через вирівнювання!
};
