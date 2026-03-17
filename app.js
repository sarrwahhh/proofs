const gallery = document.querySelector("#gallery");
const template = document.querySelector("#proof-card-template");
const proofCount = document.querySelector("#proof-count");
const updatedAt = document.querySelector("#updated-at");
const lightbox = document.querySelector("#lightbox");
const lightboxImage = document.querySelector("#lightbox-image");
const lightboxCaption = document.querySelector("#lightbox-caption");
const lightboxClose = document.querySelector("#lightbox-close");

function formatDate(value) {
  if (!value) {
    return "No date";
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(parsed);
}

function formatDateTime(value) {
  if (!value) {
    return "Waiting for uploads";
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(parsed);
}

function buildMeta(item) {
  const parts = [];

  if (item.customer) {
    parts.push(item.customer);
  }

  if (item.id) {
    parts.push(item.id);
  }

  return parts.join(" | ");
}

function openLightbox(src, altText, caption) {
  lightboxImage.src = src;
  lightboxImage.alt = altText;
  lightboxCaption.textContent = caption;
  lightbox.hidden = false;
  document.body.style.overflow = "hidden";
}

function closeLightbox() {
  lightbox.hidden = true;
  lightboxImage.src = "";
  lightboxImage.alt = "";
  lightboxCaption.textContent = "";
  document.body.style.overflow = "";
}

function attachImage(button, image, caption, title) {
  const img = button.querySelector("img");
  img.src = image.src;
  img.alt = image.alt;
  button.addEventListener("click", () => openLightbox(image.src, image.alt, `${title} - ${caption}`));
}

function renderEmptyState() {
  const card = document.createElement("article");
  card.className = "empty-state";
  card.innerHTML = `
    <div>
      <h3>No proof sets yet</h3>
      <p>Run <code>python tools/add_proof.py</code> to add your first proof and payment pair. After that, use <code>python tools/publish.py</code> to push it to GitHub Pages.</p>
    </div>
  `;
  gallery.replaceChildren(card);
}

function renderError(message) {
  const card = document.createElement("article");
  card.className = "error-state";
  card.innerHTML = `
    <div>
      <h3>Gallery data could not load</h3>
      <p>${message}</p>
    </div>
  `;
  gallery.replaceChildren(card);
}

function renderProofs(payload) {
  const items = Array.isArray(payload.items) ? payload.items : [];
  proofCount.textContent = String(items.length);
  updatedAt.textContent = formatDateTime(payload.updated_at);

  if (items.length === 0) {
    renderEmptyState();
    return;
  }

  const fragments = [];

  for (const item of items) {
    const card = template.content.firstElementChild.cloneNode(true);
    const title = item.title || "Untitled proof";
    const proofAlt = `${title} proof image`;
    const paymentAlt = `${title} payment image`;

    card.querySelector(".card-title").textContent = title;
    card.querySelector(".card-meta").textContent = buildMeta(item);
    card.querySelector(".card-date").textContent = formatDate(item.date || item.added_at);

    const note = card.querySelector(".card-note");
    if (item.note) {
      note.hidden = false;
      note.textContent = item.note;
    }

    attachImage(
      card.querySelector(".proof-button"),
      { src: item.proof_image, alt: proofAlt },
      "Proof",
      title,
    );

    attachImage(
      card.querySelector(".payment-button"),
      { src: item.payment_image, alt: paymentAlt },
      "Payment",
      title,
    );

    fragments.push(card);
  }

  gallery.replaceChildren(...fragments);
}

async function loadProofs() {
  try {
    const response = await fetch(`./data/proofs.json?v=${Date.now()}`, {
      cache: "no-store",
    });

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}.`);
    }

    const payload = await response.json();
    renderProofs(payload);
  } catch (error) {
    renderError(error.message || "Unknown error.");
  }
}

lightboxClose.addEventListener("click", closeLightbox);
lightbox.addEventListener("click", (event) => {
  if (event.target === lightbox) {
    closeLightbox();
  }
});

window.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !lightbox.hidden) {
    closeLightbox();
  }
});

loadProofs();
