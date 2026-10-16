// Static Astro build. Output goes to dist/, which Cloudflare serves (see
// wrangler.jsonc). Every page is prerendered; nothing runs on the server.
//
// SITE_URL sets canonicals, the sitemap and structured data. BASE_PATH is the
// prefix the site is served from: "" at a domain root, "/bm-industrial-solutions"
// for the GitHub Pages project URL.
import { defineConfig } from "astro/config";

const site = (process.env.SITE_URL || "https://www.bmindustrialsolutionsllc.com").replace(/\/$/, "");
const base = (process.env.BASE_PATH ?? "").replace(/\/$/, "");

export default defineConfig({
  site,
  base: base || "/",
  trailingSlash: "always",
  build: { format: "directory" },
  // Keep the HTML readable and close to the old generator's output.
  compressHTML: false,
  devToolbar: { enabled: false },
});
