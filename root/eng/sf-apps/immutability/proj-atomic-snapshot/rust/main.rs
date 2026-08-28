use arc_swap::ArcSwap;
use std::collections::HashMap;

pub struct RoutingTable {
    // комірка: ArcSwap над НЕЗМІННИМ знімком (Arc<HashMap> — ділимо, не міняємо)
    cell: ArcSwap<HashMap<String, String>>,
}

impl RoutingTable {
    pub fn new() -> Self {
        Self { cell: ArcSwap::from_pointee(HashMap::new()) }
    }

    // ЧИТАЧ: майже безкоштовний знімок, без замка
    pub fn route(&self, prefix: &str) -> Option<String> {
        self.cell.load().get(prefix).cloned()
    }

    // ПИСАР: копіюй-зміни-CAS-повтор — arc-swap уже містить цей цикл під назвою rcu()
    pub fn put(&self, prefix: &str, next_hop: &str) {
        self.cell.rcu(|cur| {
            let mut draft: HashMap<String, String> = cur.as_ref().clone();  // копія знімка
            draft.insert(prefix.to_string(), next_hop.to_string());
            draft                                                            // нова незмінна версія
        });
    }
}
