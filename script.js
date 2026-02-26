// ===== Accordion + Skill Animation JS =====
document.addEventListener("DOMContentLoaded", function () {

  const headers = document.querySelectorAll(".skill-accordion-header");

  headers.forEach(header => {
    header.addEventListener("click", () => {
      const targetId = header.getAttribute("data-target");
      const content = document.getElementById(targetId);
      const icon = header.querySelector(".toggle-icon");

      const isActive = content.classList.contains("active");

      // toggle accordion
      content.classList.toggle("active");
      header.classList.toggle("active");
      icon.textContent = isActive ? "+" : "−";

      // যদি খুলে
      if (!isActive) {
        animateSkillBars(content);
      }
    });
  });

  function animateSkillBars(container) {
    const bars = container.querySelectorAll(".skill-fill");

    bars.forEach(bar => {
      const target = parseInt(bar.dataset.width);
      const percentDisplay = bar.closest(".skill")
                                .querySelector(".skill-percent");

      // RESET
      bar.style.width = "0%";
      percentDisplay.textContent = "0%";

      let current = 0;

      const interval = setInterval(() => {
        if (current >= target) {
          clearInterval(interval);
        } else {
          current++;
          bar.style.width = current + "%";
          percentDisplay.textContent = current + "%";
        }
      }, 15);
    });
  }

});