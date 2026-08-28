// v1.0: Тривіальний тип -> передається в регістрі %rdi (System V ABI)
struct Point {
    int x;
    int y;
};
void draw_point(Point p); // Асемблер: mov rdi, [адреса]; call draw_point

// v1.1: Додано логування в деструкторі -> тип став MEMORY
struct Point {
    int x;
    int y;
    ~Point() { log("destroyed"); } // Нетривіальний деструктор!
};
void draw_point(Point p); // Асемблер: lea rdi, [rsp+8]; call draw_point
