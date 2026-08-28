enum Kind { Button, Checkbox, Scrollbar }

interface FlexFactory {
  make(kind: Kind): Product;   // ОДИН нетипізований метод замість методу-на-вид
}

// тепер новий вид не міняє сигнатуру фабрики — лише додається case всередині make.
// але ціна:
const p = factory.make(Kind.Scrollbar);
const sb = p as Scrollbar;      // downcast — статичну безпеку типів втрачено
