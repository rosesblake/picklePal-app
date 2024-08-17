document.addEventListener("DOMContentLoaded", function () {
  const stars = document.querySelectorAll(".star");
  const ratingInput = document.getElementById("rating");

  stars.forEach((star) => {
    star.addEventListener("click", function () {
      const value = this.getAttribute("data-value");
      ratingInput.value = value;

      stars.forEach((s) => {
        if (s.getAttribute("data-value") <= value) {
          s.classList.remove("text-gray-400");
          s.classList.add("text-yellow-500");
        } else {
          s.classList.remove("text-yellow-500");
          s.classList.add("text-gray-400");
        }
      });
    });
  });
});
