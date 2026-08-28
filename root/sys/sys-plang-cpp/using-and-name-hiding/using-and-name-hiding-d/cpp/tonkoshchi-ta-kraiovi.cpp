   struct BaseA { BaseA(int); };
   struct BaseB { BaseB(int); };

   struct MultiDerived : public BaseA, public BaseB {
       using BaseA::BaseA;
       using BaseB::BaseB;

       // ПОМИЛКА: MultiDerived(int) неоднозначний!
       // Щоб виправити, похідний клас мусить явно визначити власний конструктор:
       MultiDerived(int v) : BaseA(v), BaseB(v) {}
   };
