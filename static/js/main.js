//ĐĂNG NHẬP/ ĐĂNG KÝ
document.addEventListener("DOMContentLoaded", function () {
  // Lấy modal đăng nhập và đăng ký
  var loginModal = document.getElementById("loginModal");
  var loginBtn = document.getElementById("loginBtn");
  var loginClose = document.querySelector("#loginModal .close");
  var switchToRegisterBtn = document.querySelector(
    "#loginModal .button-switch"
  );

  var registerModal = document.getElementById("registerModal");
  var registerClose = document.querySelector("#registerModal .close");
  var switchToLoginBtn = document.querySelector(
    "#registerModal #switchToLoginBtn"
  );

  // Khi nút đăng nhập được click, mở modal đăng nhập
  loginBtn.onclick = function () {
    loginModal.style.display = "block";
  };

  // Khi nút (x) ở modal đăng nhập được click, đóng modal đăng nhập
  loginClose.onclick = function () {
    loginModal.style.display = "none";
  };

  // Khi nút Đăng ký tại modal đăng nhập được click, mở modal đăng ký
  switchToRegisterBtn.onclick = function () {
    loginModal.style.display = "none";
    registerModal.style.display = "block";
  };

  // Khi nút (x) ở modal đăng ký được click, đóng modal đăng ký
  registerClose.onclick = function () {
    registerModal.style.display = "none";
  };

  // Khi nút Đăng nhập tại modal đăng ký được click, mở modal đăng nhập
  switchToLoginBtn.onclick = function () {
    registerModal.style.display = "none";
    loginModal.style.display = "block";
  };

  // Khi người dùng click bên ngoài modal đăng nhập hoặc đăng ký, đóng nó
  window.onclick = function (event) {
    if (event.target == loginModal) {
      loginModal.style.display = "none";
    }
    if (event.target == registerModal) {
      registerModal.style.display = "none";
    }
  };

  // Xử lý khi form đăng nhập được gửi đi
  document
    .getElementById("loginForm")
    .addEventListener("submit", function (event) {
      event.preventDefault(); // Ngăn chặn gửi lại trang
      var formData = new FormData(this);
      var xhr = new XMLHttpRequest();
      xhr.open("POST", "/login", true);
      xhr.onload = function () {
        if (xhr.status === 200) {
          var response = JSON.parse(xhr.responseText);
          if (response.success) {
            alert(response.message);
            window.location.href = "/"; // Redirect tới trang chính
          } else {
            alert(
              "Đăng nhập không thành công. Vui lòng kiểm tra lại thông tin!"
            );
          }
        }
      };
      xhr.send(formData);
    });

  // Xử lý khi form đăng ký được gửi đi
  document
    .getElementById("registerForm")
    .addEventListener("submit", function (event) {
      event.preventDefault(); // Ngăn chặn gửi lại trang
      var formData = new FormData(this);
      var xhr = new XMLHttpRequest();
      xhr.open("POST", "/register", true);
      xhr.onload = function () {
        if (xhr.status === 200) {
          var response = JSON.parse(xhr.responseText);
          if (response.success) {
            alert(response.message); // Hiển thị thông báo đăng ký thành công
            window.location.href = "/"; // Redirect tới trang chính
          } else {
            alert(response.message); // Hiển thị thông báo lỗi
          }
        }
      };
      xhr.send(formData);
    });
});
//chức năng cho ngày tháng năm tại form đăng kí

function showDatePicker() {
  var input = document.getElementById("birthDateInput");
  input.type = "date";
  input.placeholder = "MM/DD/YYYY";
}
const detailButtons = document.querySelectorAll(".button-sale-detail");
detailButtons.forEach((button) => {
  button.addEventListener("click", function () {
    // Simulate clicking a link to a product detail page
    window.location.href = "product_detail.html";
  });
});

///PHƯƠNG THỨC THANH TOÁN
const paymentMethods = document.querySelectorAll(".payment-method");

for (const paymentMethod of paymentMethods) {
  paymentMethod.addEventListener("click", (event) => {
    const selectedPaymentMethod = event.target.value;

    // Xử lý thanh toán theo phương thức được chọn

    if (selectedPaymentMethod === "cash") {
      // Xử lý thanh toán bằng tiền mặt
    } else if (selectedPaymentMethod === "momo") {
      // Xử lý thanh toán bằng MoMo
    } else if (selectedPaymentMethod === "vnpay") {
      // Xử lý thanh toán bằng VNPay
    }
  });
}
// ADD TO CART
const decreaseBtn = document.querySelector(".decrease");
const addBtn = document.querySelector(".add");
const quantityEl = document.querySelector(".quantity");

let quantity = parseInt(quantityEl.textContent);

const updatePriceAndTotal = () => {
  const priceItems = document.querySelectorAll(".price-item");
  let totalPrice = 0;

  priceItems.forEach((priceItem) => {
    const productId = priceItem.dataset.productId;
    const quantityInput = document.querySelector(
      `.quantityInput[data-product-id="${productId}"]`
    );
    const quantity = parseInt(quantityInput.value);
    const price = parseFloat(priceItem.dataset.price);
    const itemPrice = quantity * price;
    priceItem.textContent = itemPrice.toLocaleString("vi-VN", {
      style: "currency",
      currency: "VND",
    });
    totalPrice += itemPrice;
  });

  const priceTotalEl = document.querySelector(".price-total");
  priceTotalEl.textContent = totalPrice.toLocaleString("vi-VN", {
    style: "currency",
    currency: "VND",
  });
};

// Gọi hàm updatePriceAndTotal khi trang được tải và sau mỗi lần thay đổi số lượng
document.addEventListener("DOMContentLoaded", updatePriceAndTotal);
document.querySelectorAll(".quantityInput").forEach((input) => {
  input.addEventListener("change", updatePriceAndTotal);
});

function changeQuantity(change, event) {
  document.querySelectorAll(".decrease").forEach((button) => {
    button.addEventListener("click", (event) => {
      changeQuantity(-1, event); // Gọi hàm changeQuantity với tham số -1 khi click vào nút decrease
    });
  });

  document.querySelectorAll(".add").forEach((button) => {
    button.addEventListener("click", (event) => {
      changeQuantity(1, event); // Gọi hàm changeQuantity với tham số 1 khi click vào nút add
    });
  });
  const target = event.target; // Lấy phần tử mà sự kiện được kích hoạt
  const quantityInput = target.parentNode.querySelector(".quantityInput"); // Tìm phần tử input số lượng cụ thể trong hàng

  let currentQuantity = parseInt(quantityInput.value);

  // Kiểm tra giới hạn số lượng nhỏ nhất là 1
  if (change === -1 && currentQuantity === 1) {
    return; // Không thực hiện thay đổi nếu số lượng đã là 1 và người dùng muốn giảm thêm
  }

  currentQuantity += change;

  quantityInput.value = currentQuantity;

  // Gửi request AJAX đến server để lưu số lượng vào session (sử dụng Flask)
  fetch("/change_quantity", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      productId: "{{ product['product_id'] }}",
      quantity: currentQuantity,
    }),
  });
}
const getProducts = () => {
  fetch("/products")
    .then((response) => response.json())
    .then((data) => {
      productContainer.innerHTML = "";
      for (const product of data) {
        const productElement = document.createElement("div");
        productElement.classList.add("product");

        // Use the corrected property names from the model
        productElement.innerHTML = `
          <h2>${product.product_name}</h2>
          <p>${product.product_description}</p>
          <p>${product.product_price.toLocaleString("vi-VN", {
            style: "currency",
            currency: "VND",
          })}</p>
          <img src="${product.product_image}">
        `;

        productContainer.appendChild(productElement);
      }
    });
};
$(document).ready(function () {
  updatePriceAndTotal();
});

// chức năng chỉnh sửa profile người dùng

function editField(event, fieldName) {
  event.preventDefault(); // Ngăn chặn hành vi mặc định của button

  var field = document.querySelector(`[name=${fieldName}]`);
  var editButton = field.nextElementSibling; // Lấy button "Chỉnh sửa" kế tiếp của trường

  if (field.disabled) {
    field.disabled = false; // Cho phép chỉnh sửa
    editButton.textContent = ""; // Thay đổi nội dung của button thành "Lưu"
  } else {
    field.disabled = true; // Không cho phép chỉnh sửa
    editButton.textContent = "Chỉnh sửa"; // Thay đổi nội dung của button thành "Chỉnh sửa"
    updateUserInfo(fieldName, field.value); // Gọi hàm cập nhật thông tin người dùng
  }
}
//End chức năng chỉnh sửa profile người dùng
document
  .querySelector(".button-complete")
  .addEventListener("click", function () {
    fetch("/place_order", {
      method: "POST",
      body: new FormData(document.getElementById("delivery")),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          alert(data.message);
        } else {
          alert(data.message);
        }
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  });
