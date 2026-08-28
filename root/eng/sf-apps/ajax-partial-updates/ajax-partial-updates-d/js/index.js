// Класичний патерн XMLHttpRequest
const xhr = new XMLHttpRequest();
xhr.open("GET", "/api/products?category=books", true);
xhr.setRequestHeader("Accept", "application/json");

xhr.onreadystatechange = function () {
  if (xhr.readyState === 4) {
    if (xhr.status >= 200 && xhr.status < 300) {
      const data = JSON.parse(xhr.responseText);
      renderProductList(data);
    } else {
      showErrorMessage("Помилка завантаження даних");
    }
  }
};

xhr.onerror = function () {
  showErrorMessage("Помилка мережевого з'єднання");
};

xhr.send(null);
