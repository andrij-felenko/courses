// Синхронізація фонового оновлення з адресою сторінки
async function navigateToCategory(categoryId: number, pushHistory = true): Promise<void> {
  const url = `/catalog?category=${categoryId}`;
  const success = await engine.updateElement('main-content', '#products-grid', `/partials${url}`);

  if (success && pushHistory) {
    history.pushState({ categoryId }, '', url);
  }
}

window.addEventListener('popstate', (event) => {
  if (event.state?.categoryId) {
    navigateToCategory(event.state.categoryId, false);
  }
});
