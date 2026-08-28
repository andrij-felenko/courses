// Пакет billing (політика) оголошує ВЛАСНИЙ інтерфейс — рівно те, що йому треба.
package billing

type Ledger interface {          // інтерфейс живе у СПОЖИВАЧА
    Record(entry Entry) error
}

type Invoicer struct {
    ledger Ledger                // залежить від своєї ж абстракції
}

func (i *Invoicer) Charge(o Order) error {
    return i.ledger.Record(entryFor(o))
}
