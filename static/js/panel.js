document.addEventListener("DOMContentLoaded", function () {
  const modalBackdrop = document.getElementById("replyModalBackdrop");
  const closeBtn = document.getElementById("closeReplyModal");
  const cancelBtn = document.getElementById("cancelReplyModal");
  const form = document.getElementById("replyModalForm");
  const textarea = document.getElementById("modalReplyTextarea");

  const nameEl = document.getElementById("modalMsgName");
  const emailEl = document.getElementById("modalMsgEmail");
  const phoneEl = document.getElementById("modalMsgPhone");
  const subjectEl = document.getElementById("modalMsgSubject");
  const messageEl = document.getElementById("modalMsgMessage");
  const submitBtn = document.getElementById("submitReplyBtn");

  if (
    !modalBackdrop ||
    !closeBtn ||
    !cancelBtn ||
    !form ||
    !textarea ||
    !nameEl ||
    !emailEl ||
    !phoneEl ||
    !subjectEl ||
    !messageEl ||
    !submitBtn
  ) {
    return;
  }

  function openModal(button) {
    const id = button.dataset.msgId || "";
    const name = button.dataset.msgName || "";
    const email = button.dataset.msgEmail || "";
    const phone = button.dataset.msgPhone || "";
    const subject = button.dataset.msgSubject || "";
    const message = button.dataset.msgMessage || "";
    const replied = button.dataset.msgReplied === "1";
    const reply = button.dataset.msgReply || "";

    nameEl.textContent = name;
    emailEl.textContent = email;
    phoneEl.textContent = phone || "—";
    subjectEl.textContent = subject;
    messageEl.textContent = message;

    form.action = `/panel/mensajes/${id}/responder/`;

    if (replied) {
      textarea.value = reply;
      textarea.setAttribute("readonly", "readonly");
      textarea.required = false;
      submitBtn.style.display = "none";
    } else {
      textarea.value = "";
      textarea.removeAttribute("readonly");
      textarea.required = true;
      submitBtn.style.display = "inline-flex";
    }

    modalBackdrop.classList.add("show");
    document.body.style.overflow = "hidden";
  }

  function closeModal() {
    modalBackdrop.classList.remove("show");
    document.body.style.overflow = "";
  }

  document.querySelectorAll(".open-reply-modal").forEach((btn) => {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      openModal(this);
    });
  });

  closeBtn.addEventListener("click", closeModal);
  cancelBtn.addEventListener("click", closeModal);

  modalBackdrop.addEventListener("click", function (e) {
    if (e.target === modalBackdrop) {
      closeModal();
    }
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && modalBackdrop.classList.contains("show")) {
      closeModal();
    }
  });
});