const gallery = document.querySelector("#gallery");
const template = document.querySelector("#proof-card-template");
const proofCount = document.querySelector("#proof-count");
const updatedAt = document.querySelector("#updated-at");
const lightbox = document.querySelector("#lightbox");
const lightboxImage = document.querySelector("#lightbox-image");
const lightboxCaption = document.querySelector("#lightbox-caption");
const lightboxClose = document.querySelector("#lightbox-close");

function cloneValue(value) {
  return JSON.parse(JSON.stringify(value));
}

function readList(selector) {
  return Array.from(document.querySelectorAll(`${selector} li`), (item) => item.textContent.trim());
}

function readTerms() {
  return Array.from(document.querySelectorAll("#terms-grid .term-item"), (item) => ({
    label: item.querySelector(".term-label")?.textContent.trim() || "",
    value: item.querySelector("strong")?.textContent.trim() || "",
  }));
}

const defaultSiteContent = {
  hero: {
    pill: document.querySelector("#hero-pill")?.textContent.trim() || "",
    title: document.querySelector("#hero-title")?.textContent.trim() || "",
    subtitle: document.querySelector("#hero-subtitle")?.textContent.trim() || "",
  },
  stats: {
    count_label: document.querySelector("#proof-count-label")?.textContent.trim() || "",
    updated_label: document.querySelector("#updated-label")?.textContent.trim() || "",
    layout_value: document.querySelector("#layout-value")?.textContent.trim() || "",
    layout_label: document.querySelector("#layout-label")?.textContent.trim() || "",
  },
  gallery: {
    kicker: document.querySelector("#gallery-kicker")?.textContent.trim() || "",
    title: document.querySelector("#gallery-title")?.textContent.trim() || "",
    note: document.querySelector("#gallery-note")?.textContent.trim() || "",
    empty_title: "No proof sets yet",
    empty_body: "Your proof and payment pairs will appear here after the first upload.",
  },
  overview: {
    pill: document.querySelector("#overview-pill")?.textContent.trim() || "",
    title: document.querySelector("#overview-title")?.textContent.trim() || "",
    note: document.querySelector("#overview-note")?.textContent.trim() || "",
  },
  details: {
    benefits: {
      title: document.querySelector("#benefits-title")?.textContent.trim() || "",
      items: readList("#benefits-list"),
    },
    privacy: {
      title: document.querySelector("#privacy-title")?.textContent.trim() || "",
      items: readList("#privacy-list"),
    },
    terms: {
      title: document.querySelector("#terms-title")?.textContent.trim() || "",
      items: readTerms(),
    },
  },
};

let currentSiteContent = cloneValue(defaultSiteContent);

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

function setText(selector, value) {
  const element = document.querySelector(selector);
  if (element && typeof value === "string") {
    element.textContent = value;
  }
}

function renderList(selector, items) {
  const list = document.querySelector(selector);
  if (!list || !Array.isArray(items)) {
    return;
  }

  const rows = items
    .filter((item) => typeof item === "string" && item.trim())
    .map((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      return li;
    });

  if (rows.length > 0) {
    list.replaceChildren(...rows);
  }
}

function renderTerms(items) {
  const termsGrid = document.querySelector("#terms-grid");
  if (!termsGrid || !Array.isArray(items)) {
    return;
  }

  const rows = items
    .filter((item) => item && (item.label || item.value))
    .map((item) => {
      const wrapper = document.createElement("div");
      wrapper.className = "term-item";

      const label = document.createElement("span");
      label.className = "term-label";
      label.textContent = item.label || "";

      const value = document.createElement("strong");
      value.textContent = item.value || "";

      wrapper.append(label, value);
      return wrapper;
    });

  if (rows.length > 0) {
    termsGrid.replaceChildren(...rows);
  }
}

function describeImageShape(img) {
  const width = img.naturalWidth;
  const height = img.naturalHeight;

  if (!width || !height) {
    return "unknown";
  }

  const ratio = width / height;

  if (ratio >= 1.25) {
    return "landscape";
  }

  if (ratio <= 0.85) {
    return "portrait";
  }

  return "square";
}

function updatePairLayout(pair) {
  if (!pair) {
    return;
  }

  const buttons = Array.from(pair.querySelectorAll(".image-button"));
  const shapes = buttons.map((button) => button.dataset.shape || "unknown");

  if (shapes.some((shape) => shape === "unknown")) {
    return;
  }

  const landscapeCount = shapes.filter((shape) => shape === "landscape").length;
  const portraitCount = shapes.filter((shape) => shape === "portrait").length;
  const shouldStack = landscapeCount > 0 && (portraitCount > 0 || landscapeCount === shapes.length);

  pair.classList.toggle("image-pair--stacked", shouldStack);
}

function syncImagePresentation(button, img) {
  const shape = describeImageShape(img);
  const card = button.closest(".image-card");
  const pair = button.closest(".image-pair");

  button.dataset.shape = shape;
  button.classList.toggle("image-button--portrait", shape === "portrait");
  button.classList.toggle("image-button--landscape", shape === "landscape");
  button.classList.toggle("image-button--square", shape === "square");

  if (card) {
    card.dataset.shape = shape;
    card.classList.toggle("image-card--portrait", shape === "portrait");
    card.classList.toggle("image-card--landscape", shape === "landscape");
    card.classList.toggle("image-card--square", shape === "square");
  }

  updatePairLayout(pair);
}

function renderSiteContent(content) {
  currentSiteContent = cloneValue(content);

  setText("#hero-pill", content.hero?.pill);
  setText("#hero-title", content.hero?.title);
  setText("#hero-subtitle", content.hero?.subtitle);

  setText("#proof-count-label", content.stats?.count_label);
  setText("#updated-label", content.stats?.updated_label);
  setText("#layout-value", content.stats?.layout_value);
  setText("#layout-label", content.stats?.layout_label);

  setText("#gallery-kicker", content.gallery?.kicker);
  setText("#gallery-title", content.gallery?.title);
  setText("#gallery-note", content.gallery?.note);

  setText("#overview-pill", content.overview?.pill);
  setText("#overview-title", content.overview?.title);
  setText("#overview-note", content.overview?.note);

  setText("#benefits-title", content.details?.benefits?.title);
  renderList("#benefits-list", content.details?.benefits?.items || []);

  setText("#privacy-title", content.details?.privacy?.title);
  renderList("#privacy-list", content.details?.privacy?.items || []);

  setText("#terms-title", content.details?.terms?.title);
  renderTerms(content.details?.terms?.items || []);
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

function attachImage(button, image, caption) {
  const img = button.querySelector("img");
  img.src = image.src;
  img.alt = image.alt;
  img.loading = "lazy";

  const syncPresentation = () => syncImagePresentation(button, img);
  if (img.complete && img.naturalWidth) {
    syncPresentation();
  } else {
    img.addEventListener("load", syncPresentation, { once: true });
  }

  button.addEventListener("click", () => openLightbox(image.src, image.alt, caption));
}

function renderEmptyState() {
  const card = document.createElement("article");
  card.className = "empty-state";
  card.innerHTML = `
    <div>
      <h3>${currentSiteContent.gallery?.empty_title || "No proof sets yet"}</h3>
      <p>${currentSiteContent.gallery?.empty_body || "Your proof and payment pairs will appear here after the first upload."}</p>
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
    const proofAlt = "Proof image";
    const paymentAlt = "Payment image";

    const note = card.querySelector(".card-note");
    if (item.note) {
      note.hidden = false;
      note.textContent = item.note;
    }

    attachImage(
      card.querySelector(".proof-button"),
      { src: item.proof_image, alt: proofAlt },
      "Proof",
    );

    attachImage(
      card.querySelector(".payment-button"),
      { src: item.payment_image, alt: paymentAlt },
      "Payment",
    );

    fragments.push(card);
  }

  gallery.replaceChildren(...fragments);
}

async function loadSiteContent() {
  const response = await fetch(`./data/site_content.json?v=${Date.now()}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Site content request failed with status ${response.status}.`);
  }

  const payload = await response.json();
  renderSiteContent(payload);
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

async function loadPage() {
  const siteContentResult = await loadSiteContent().catch((error) => {
    console.error(error);
  });

  await loadProofs();
  return siteContentResult;
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

loadPage();
