   struct BaseShape {
       virtual constexpr double area() const = 0;
       virtual ~BaseShape() = default;
   };

   struct Square : BaseShape {
       double side;
       constexpr explicit Square(double s) : side(s) {}
       constexpr double area() const override { return side * side; }
   };

   constexpr double get_area(const BaseShape& shape) {
       return shape.area(); // Віртуальний виклик резолвиться компілятором!
   }

   constexpr Square sq(4.0);
   static_assert(get_area(sq) == 16.0);
