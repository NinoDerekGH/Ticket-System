function validateForm() {
    var firstname = document.getElementById("fname").value;
    var firstnameError = document.getElementById("fname-error");
    var lastname = document.getElementById("lname").value;
    var lastnameError = document.getElementById("lname-error");
    var username = document.getElementById("uname").value;
    var usernameError = document.getElementById("uname-error");
    var password = document.getElementById("pwd").value;
    var passwordError = document.getElementById("password-error");

    if (firstname === "") {
      firstnameError.insertAdjacentHTML("beforeend", "Field is required!");
    }
    if (lastname === "") {
      lastnameError.insertAdjacentHTML("beforeend", "Field is required!");
    }
    if (username === "") {
      usernameError.insertAdjacentHTML("beforeend", "Field is required!");
    }
    if (password === "") {
      passwordError.insertAdjacentHTML("beforeend", "Field is required!");
    }
  }