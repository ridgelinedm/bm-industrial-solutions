// URL and text helpers shared by every component.
const RAW_BASE = import.meta.env.BASE_URL.replace(/\/$/, "");

/** Path prefix the site is served from ("" at a domain root). */
export const BASE = RAW_BASE;

/** Absolute site URL without a trailing slash, for canonicals and schema. */
export const SITE_URL = (import.meta.env.SITE as string).replace(/\/$/, "") + RAW_BASE;

/** Root-relative URL. `path` is "" for home, else "services/foo". */
export function url(path: string): string {
  const p = path.replace(/^\/+|\/+$/g, "");
  return p ? `${BASE}/${p}/` : `${BASE}/`;
}

/** Root-relative URL for a file under public/. */
export function asset(path: string): string {
  return `${BASE}/${path.replace(/^\/+/, "")}`;
}

export function canonical(path: string): string {
  const p = path.replace(/^\/+|\/+$/g, "");
  return p ? `${SITE_URL}/${p}/` : `${SITE_URL}/`;
}

/** Plain text from an HTML fragment (for aria-labels and schema). */
export function stripTags(s: string): string {
  return s
    .replace(/<[^>]+>/g, "")
    .replace(/&nbsp;/g, " ")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#x27;|&#39;/g, "'")
    .replace(/&amp;/g, "&")
    .trim();
}

/** Turns "foo" into an internal URL; leaves tel:, mailto: and http links alone. */
export function href(target: string): string {
  return /^(tel:|mailto:|https?:)/.test(target) ? target : url(target);
}
