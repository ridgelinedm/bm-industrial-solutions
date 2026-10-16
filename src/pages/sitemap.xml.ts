// sitemap.xml, built from the same data as the pages.
import { SERVICES, AREAS } from "../data/content";
import { canonical } from "../lib/site";

const PAGES = ["", "services", ...SERVICES.map((s) => s.path), "service-areas", ...AREAS.map((a) => a.path), "about", "contact"];

export function GET() {
  // Home and top-level hubs get more weight than deep leaves.
  const urls = PAGES.map((p) => {
    const depth = p ? p.split("/").length : 0;
    const priority = ({ 0: "1.0", 1: "0.9", 2: "0.8" } as Record<number, string>)[depth] ?? "0.7";
    return `  <url><loc>${canonical(p)}</loc><changefreq>monthly</changefreq><priority>${priority}</priority></url>`;
  });
  const xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls.join("\n") + "\n</urlset>\n";
  return new Response(xml, { headers: { "Content-Type": "application/xml" } });
}
