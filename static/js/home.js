document.addEventListener("DOMContentLoaded", function () {
  new Swiper(".heroSwiper", {
    loop: true,
    speed: 900,
    autoplay: {
      delay: 4500,
      disableOnInteraction: false,
    },
    pagination: {
      el: ".hero-pagination",
      clickable: true,
    },
    navigation: {
      nextEl: ".hero-button-next",
      prevEl: ".hero-button-prev",
    },
  });

  new Swiper(".mySwiper", {
    loop: false,
    speed: 600,
    spaceBetween: 20,
    grabCursor: true,
    allowTouchMove: true,
    watchOverflow: true,
    navigation: {
      nextEl: ".mySwiper .swiper-button-next",
      prevEl: ".mySwiper .swiper-button-prev",
    },
    breakpoints: {
      0: { slidesPerView: 1 },
      576: { slidesPerView: 2 },
      768: { slidesPerView: 3 },
      1200: { slidesPerView: 4 }
    }
  });
});