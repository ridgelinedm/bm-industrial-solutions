// schema.org structured data, emitted as JSON-LD in each page's <head>.
import { BRANDS, COMPANY, SERVICES, type Faq } from "../data/content";
import { SITE_URL, canonical, stripTags } from "./site";

const STATES = ["South Carolina", "Georgia", "North Carolina"];
export const statesServed = () => STATES.map((name) => ({ "@type": "State", name }));

export function localBusinessSchema() {
  return {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "@id": SITE_URL + "/#business",
    name: COMPANY.name,
    legalName: COMPANY.legal_name,
    url: SITE_URL + "/",
    telephone: COMPANY.phone,
    email: COMPANY.email,
    image: SITE_URL + "/assets/img/og-image.jpg",
    logo: SITE_URL + "/assets/img/logo/logo-full-color.png",
    slogan: COMPANY.tagline,
    founder: { "@type": "Person", name: COMPANY.owner },
    // No street address is published, so the schema stays at locality level.
    address: {
      "@type": "PostalAddress",
      addressLocality: COMPANY.city,
      addressRegion: COMPANY.state,
      postalCode: COMPANY.zip,
      addressCountry: "US",
    },
    openingHoursSpecification: [{
      "@type": "OpeningHoursSpecification",
      dayOfWeek: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
      opens: "00:00",
      closes: "23:59",
    }],
    areaServed: statesServed(),
    knowsAbout: BRANDS,
    hasOfferCatalog: {
      "@type": "OfferCatalog",
      name: "Industrial services",
      itemListElement: SERVICES.map((s) => ({
        "@type": "Offer",
        itemOffered: { "@type": "Service", name: s.title, url: canonical(s.path) },
      })),
    },
  };
}

export function faqSchema(items: Faq[]) {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: items.map(([q, a]) => ({
      "@type": "Question",
      name: q,
      acceptedAnswer: { "@type": "Answer", text: stripTags(a) },
    })),
  };
}

export function breadcrumbSchema(trail: [string, string | null][]) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: trail.map(([name, path], i) => ({
      "@type": "ListItem",
      position: i + 1,
      name,
      ...(path !== null ? { item: canonical(path) } : {}),
    })),
  };
}
