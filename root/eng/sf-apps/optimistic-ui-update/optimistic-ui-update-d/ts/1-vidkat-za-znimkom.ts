// Псевдокод знімка мутації
const previousState = clone(store.getState().todos);

try {
  store.setState(applyOptimisticUpdate(previousState, action));
  await api.saveTodo(action.payload);
} catch (error) {
  // Відкат: тупе відновлення знімка
  store.setState(previousState);
  showToast("Не вдалося зберегти завдання");
}
