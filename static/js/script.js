function validateForm() {
    var email = document.getElementById("email").value;
    var emailError = document.getElementById("email-error");
    var password = document.getElementById("pwd").value;
    var passwordError = document.getElementById("password-error");
    if (email === "") {
      emailError.insertAdjacentHTML("beforeend", "Email field is required!");
    }
    if (password === "") {
      passwordError.insertAdjacentHTML("beforeend", "Password field is required!");
    }
  }