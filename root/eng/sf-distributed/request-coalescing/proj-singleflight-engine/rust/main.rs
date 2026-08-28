use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::{broadcast, Mutex};

#[derive(Clone)]
pub struct SingleFlight<K, V> {
    table: Arc<Mutex<HashMap<K, broadcast::Sender<Result<V, String>>>>>,
}

impl<K, V> SingleFlight<K, V>
where
    K: std::hash::Hash + Eq + Clone + Send + 'static,
    V: Clone + Send + 'static,
{
    pub fn new() -> Self {
        Self {
            table: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    pub async fn execute<F, Fut>(&self, key: K, f: F) -> Result<V, String>
    where
        F: FnOnce() -> Fut,
        Fut: std::future::Future<Output = Result<V, String>> + Send + 'static,
    {
        let mut rx = {
            let mut table = self.table.lock().await;
            if let Some(tx) = table.get(&key) {
                // Рейс вже в польоті: підписуємось на канал
                tx.subscribe()
            } else {
                // Стаємо лідером рейсу
                let (tx, rx) = broadcast::channel(1);
                table.insert(key.clone(), tx.clone());
                drop(table);

                let table_clone = self.table.clone();
                let key_clone = key.clone();

                tokio::spawn(async move {
                    let result = f().await;
                    let _ = tx.send(result);
                    let mut table = table_clone.lock().await;
                    table.remove(&key_clone);
                });

                rx
            }
        };

        match rx.recv().await {
            Ok(res) => res,
            Err(e) => Err(format!("Broadcast receive error: {:?}", e)),
        }
    }
}
