document.querySelectorAll(".faq__entry").forEach((faq) => {
    faq.addEventListener("click", () => {
      // Close other open FAQs (optional: remove if you want multiple open)
      document.querySelectorAll(".faq__entry").forEach((item) => {
        if (item !== faq) {
          item.classList.remove("active");
          item.querySelector(".faq__answer").style.maxHeight = null;
        }
      });

      // Toggle current FAQ
      faq.classList.toggle("active");
      const answer = faq.querySelector(".faq__answer");

      if (faq.classList.contains("active")) {
        answer.style.maxHeight = answer.scrollHeight + "px"; // fit to content
      } else {
        answer.style.maxHeight = null;
      }
    });
  });
 document.addEventListener("DOMContentLoaded", function () {
    const sections = document.querySelectorAll("section");

    const observer = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
        }
      });
    }, { threshold: 0.2 });

    sections.forEach(section => {
      observer.observe(section);
    });
  });



const iconButtons = document.querySelectorAll(".about__icon-btn");

iconButtons.forEach(btn => {
  btn.addEventListener("mouseenter", () => {
    // Get the corresponding text id
    const textId = "text-" + btn.dataset.text;
    const textElement = document.getElementById("text-" + btn.dataset.text);
    
    // Add active class to show text
    if (!textElement.classList.contains("active")) {
      textElement.classList.add("active");
    }
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const aboutSection = document.querySelector(".about");

  const observer = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          aboutSection.classList.add("animate"); 
          observer.unobserve(aboutSection); 
        }
      });
    },
    { threshold: 0.2 }
  );

  observer.observe(aboutSection);
});

document.addEventListener("DOMContentLoaded", () => {
  const explore = document.querySelector("#explore");

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        explore.classList.add("animate");
        observer.unobserve(explore); // run only once
      }
    });
  }, { threshold: 0.3 }); // trigger when 30% visible

  observer.observe(explore);
});