async function toggleAvailability(day, period, event) {
  // Ensure event is defined and use event.currentTarget to reference the clicked element
  const cell = event.currentTarget;
  const isSelected = cell.classList.contains("bg-dark-green");

  // Toggle availability
  cell.classList.toggle("bg-dark-green", !isSelected);
  cell.classList.toggle("bg-gray-200", isSelected);

  try {
    const res = await fetch("/profile/schedule", {
      method: "POST",
      body: JSON.stringify({ day, period, selected: !isSelected }),
      headers: {
        "Content-Type": "application/json",
      },
    });
    if (!res.ok) {
      throw new Error("Network response was not ok");
    }

    const data = await res.json();
    console.log("Server response:", data);
  } catch (error) {
    console.error("Error:", error);
  }
}
