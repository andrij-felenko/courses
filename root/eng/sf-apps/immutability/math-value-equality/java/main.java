class Tag {                         // «значення», але МІНЛИВЕ — у цьому вся біда
    String name;
    Tag(String n) { name = n; }
    @Override public boolean equals(Object o) {
        return o instanceof Tag t && t.name.equals(name);
    }
    @Override public int hashCode() { return name.hashCode(); }
}

var set = new HashSet<Tag>();
var a = new Tag("cola");
set.add(a);                         // лягає в кошик геш("cola")
a.name = "beer";                    // мутація поля, що бере участь у геші

set.contains(a);                    // false — той самий об'єкт «не в множині»!
set.iterator().next() == a;         // true  — а перебором він ось він, тут
