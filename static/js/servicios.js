
  document.querySelectorAll(".faq-question").forEach((btn) => {
    btn.addEventListener("click", () => {
      const item = btn.closest(".faq-item");
      const isOpen = item.classList.contains("open");

      document.querySelectorAll(".faq-item").forEach((el) => {
        el.classList.remove("open");
        const icon = el.querySelector(".faq-icon");
        if (icon) icon.textContent = "+";
      });

      if (!isOpen) {
        item.classList.add("open");
        const icon = item.querySelector(".faq-icon");
        if (icon) icon.textContent = "−";
      }
    });
  });


document.addEventListener('DOMContentLoaded', function () {
    const headers = document.querySelectorAll('.accordion-header-sn');

    headers.forEach(header => {
      header.addEventListener('click', function () {
        const item = this.parentElement;
        const body = item.querySelector('.accordion-body-sn');
        const icon = item.querySelector('.icon-sn');
        const parentAccordion = item.parentElement;
        const isActive = item.classList.contains('active');

        parentAccordion.querySelectorAll('.accordion-item-sn').forEach(el => {
          el.classList.remove('active');
          const elBody = el.querySelector('.accordion-body-sn');
          const elIcon = el.querySelector('.icon-sn');
          if (elBody) elBody.style.display = 'none';
          if (elIcon) elIcon.textContent = '+';
        });

        if (!isActive) {
          item.classList.add('active');
          body.style.display = 'block';
          icon.textContent = '−';
        }
      });
    });
  });


  document.querySelectorAll('.dp-toggle-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      const card = this.closest('.dp-card-expand');
      const isActive = card.classList.contains('active');

      document.querySelectorAll('.dp-card-expand').forEach(function(item) {
        item.classList.remove('active');
        const button = item.querySelector('.dp-toggle-btn');
        if (button) {
          button.textContent = 'Ver más';
        }
      });

      if (!isActive) {
        card.classList.add('active');
        this.textContent = 'Ver menos';
      }
    });
  });



  document.querySelectorAll(".tc-question").forEach((btn) => {
    btn.addEventListener("click", () => {
      const item = btn.closest(".tc-item");
      const isOpen = item.classList.contains("open");

      document.querySelectorAll(".tc-item").forEach((el) => {
        el.classList.remove("open");
        const icon = el.querySelector(".tc-icon");
        if (icon) icon.textContent = "+";
      });

      if (!isOpen) {
        item.classList.add("open");
        const icon = item.querySelector(".tc-icon");
        if (icon) icon.textContent = "−";
      }
    });
  });



  document.querySelectorAll('.ep-card-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      const card = this.closest('.ep-card');
      const isActive = card.classList.contains('active');

      document.querySelectorAll('.ep-card').forEach(function(item) {
        item.classList.remove('active');
        const button = item.querySelector('.ep-card-btn');
        if (button) {
          button.textContent = 'Ver más';
        }
      });

      if (!isActive) {
        card.classList.add('active');
        this.textContent = 'Ver menos';
      }
    });
  });


  document.querySelectorAll('.cbr-card-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const card = btn.closest('.cbr-card');
      card.classList.toggle('active');
      btn.textContent = card.classList.contains('active') ? 'Ver menos' : 'Ver más';
    });
  });


