const getStarted = document.querySelector("#enter-btn");
const h1Container = document.querySelector(".h1-container");

getStarted.addEventListener("click", function (e) {
  e.preventDefault();
  if (e.target.id === "enter-btn") {
    h1Container.innerHTML = "";
    loginPage();
  }
});

function loginPage() {
  const div = document.createElement("div");
  div.innerHTML = `
    <h1>LOGIN</h1>
    <form id='login'>
      <label for="email">EMAIL:</label>
      <br>
      <input type="email" id="email" placeholder="enter email">
      <br>
      <label for="password" id="p-label">PASSWORD:</label>
      <input type="password" id="password" placeholder="enter password">
      <br>
      <button type="submit" id="login-btn">LOGIN</button>
      <br>
      <a href="#">CREATE AN ACCOUNT</a>
    </form>`;
  h1Container.appendChild(div);

  // Add event listener for login button after it's created
  document.querySelector("#login-btn").addEventListener("click", function (e) {
    e.preventDefault();
    loginUser();
  });
}

function loginUser() {
  console.log("Login button clicked");
}
