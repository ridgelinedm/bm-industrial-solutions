/* BM Industrial Solutions: progressive enhancement only.
   Every page works with JS disabled; this adds the drawer, sticky nav state,
   scroll reveals, and the contact form submit handler. */
(function () {
  "use strict";

  /* --- Mobile drawer ----------------------------------------------------- */
  var toggle = document.querySelector(".nav__toggle");
  var drawer = document.getElementById("drawer");

  function setDrawer(open) {
    if (!toggle || !drawer) return;
    toggle.setAttribute("aria-expanded", String(open));
    drawer.classList.toggle("is-open", open);
    document.body.style.overflow = open ? "hidden" : "";
  }

  if (toggle && drawer) {
    toggle.addEventListener("click", function () {
      setDrawer(toggle.getAttribute("aria-expanded") !== "true");
    });
    drawer.addEventListener("click", function (e) {
      if (e.target.closest("a")) setDrawer(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") setDrawer(false);
    });
    window.addEventListener("resize", function () {
      if (window.innerWidth > 1040) setDrawer(false);
    });
  }

  /* --- Sticky nav shadow ------------------------------------------------- */
  var nav = document.querySelector(".nav");
  if (nav) {
    var onScroll = function () {
      nav.classList.toggle("is-stuck", window.scrollY > 8);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* --- Scroll reveal ----------------------------------------------------- */
  var reveals = document.querySelectorAll(".reveal");

  // Show an element, then retire the reveal classes once its entrance is
  // done, so the element's own hover and press transforms apply again (the
  // settled reveal state would otherwise pin transform: none over them).
  function show(el) {
    if (el.classList.contains("is-in")) return;
    el.classList.add("is-in");
    var retire = function () {
      el.removeEventListener("transitionend", onEnd);
      el.classList.remove("reveal", "is-in");
    };
    var onEnd = function (e) { if (e.target === el && e.propertyName === "opacity") retire(); };
    el.addEventListener("transitionend", onEnd);
    setTimeout(retire, 1200);
  }
  var motionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  var reduced = motionQuery.matches;

  // If reduced motion is switched on while the page is open, show anything
  // still waiting to reveal rather than animating it later.
  if (motionQuery.addEventListener) {
    motionQuery.addEventListener("change", function (e) {
      if (!e.matches) return;
      document.querySelectorAll(".reveal:not(.is-in)").forEach(function (el) {
        show(el);
      });
    });
  }

  if (!reveals.length) {
    /* nothing to do */
  } else if (reduced || !("IntersectionObserver" in window)) {
    reveals.forEach(show);
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        show(entry.target);
        io.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.06 });
    reveals.forEach(function (el) { io.observe(el); });

    // Backstop: if the observer has not delivered for something after a few
    // seconds (headless capture, an odd viewport, a throttled tab), show it
    // anyway. Content must never be permanently invisible.
    setTimeout(function () {
      document.querySelectorAll(".reveal:not(.is-in)").forEach(function (el) {
        show(el);
      });
    }, 2500);
  }

  /* --- Contact form ------------------------------------------------------
     Posts to the endpoint in data-endpoint when one is configured. Until the
     owner wires up a form service, it falls back to composing an email so the
     form is never a dead end. */
  var form = document.querySelector("form[data-contact-form]");
  if (form) {
    var status = form.querySelector(".form__status");

    var say = function (msg, ok) {
      if (!status) return;
      status.textContent = msg;
      status.className = "form__status is-visible form__status--" + (ok ? "ok" : "err");
    };

    form.addEventListener("submit", function (e) {
      // Honeypot: bots fill hidden fields, humans don't.
      var hp = form.querySelector('input[name="_gotcha"]');
      if (hp && hp.value) { e.preventDefault(); return; }

      var endpoint = form.getAttribute("data-endpoint") || "";
      var configured = endpoint && endpoint.indexOf("YOUR_FORM_ID") === -1;

      if (!configured) {
        e.preventDefault();
        var get = function (n) {
          var f = form.querySelector('[name="' + n + '"]');
          return f ? f.value.trim() : "";
        };
        var body = [
          "Name: " + get("name"),
          "Company: " + get("company"),
          "Phone: " + get("phone"),
          "Email: " + get("email"),
          "Service needed: " + get("service"),
          "Urgency: " + get("urgency"),
          "",
          get("message")
        ].join("\n");
        window.location.href =
          "mailto:" + form.getAttribute("data-fallback-email") +
          "?subject=" + encodeURIComponent("Website quote request: " + (get("name") || "New enquiry")) +
          "&body=" + encodeURIComponent(body);
        say("Opening your email app with the details filled in. If nothing happens, call 843-401-9670.", true);
        return;
      }

      e.preventDefault();
      var btn = form.querySelector('button[type="submit"]');
      if (btn) { btn.disabled = true; btn.setAttribute("aria-busy", "true"); btn.textContent = "Sending…"; }

      fetch(endpoint, {
        method: "POST",
        body: new FormData(form),
        headers: { Accept: "application/json" }
      }).then(function (res) {
        if (!res.ok) throw new Error("bad status");
        form.reset();
        say("Thanks, your request is in. We answer every enquiry within one business day, or immediately if you marked it an emergency.", true);
      }).catch(function () {
        say("That didn't go through. Please call 843-401-9670 or email bmindustrialsolutionsllc@gmail.com.", false);
      }).finally(function () {
        if (btn) { btn.disabled = false; btn.removeAttribute("aria-busy"); btn.textContent = "Send request"; }
      });
    });
  }

  /* --- Current year ------------------------------------------------------ */
  var y = document.getElementById("year");
  if (y) y.textContent = String(new Date().getFullYear());
})();
