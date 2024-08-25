async function likePost(button) {
  const postId = button.getAttribute("data-post-id");

  try {
    const response = await fetch(`/posts/${postId}/like`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": document
          .querySelector('meta[name="csrf-token"]')
          .getAttribute("content"),
      },
      body: JSON.stringify({ postId: postId }),
    });

    if (response.ok) {
      // Update the text content of the span within the clicked button
      const span = button.querySelector(".like-text");
      if (span.textContent === "Like") {
        span.textContent = "Liked"; // Change the text content to "Liked"
      } else {
        span.textContent = "Like";
      }
      console.log("Post liked successfully!");
    } else {
      console.error("Failed to like post:", await response.text());
    }
  } catch (error) {
    console.error("Error:", error);
  }
}
