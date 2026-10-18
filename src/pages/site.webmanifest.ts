// Web app manifest (Android home-screen icon and name). Built here so the
// icon paths follow BASE_PATH.
import { COMPANY } from "../data/content";
import { asset } from "../lib/site";

export function GET() {
  const icon = (file: string, sizes: string, purpose?: string) => ({
    src: asset(`assets/img/logo/${file}`), sizes, type: "image/png", ...(purpose ? { purpose } : {}),
  });
  const manifest = {
    name: COMPANY.name,
    short_name: "BM Industrial",
    icons: [
      icon("android-chrome-192x192.png", "192x192"),
      icon("android-chrome-512x512.png", "512x512"),
      icon("maskable-icon-512x512.png", "512x512", "maskable"),
    ],
    theme_color: "#231f20",
    background_color: "#ffffff",
    display: "standalone",
  };
  return new Response(JSON.stringify(manifest, null, 2), { headers: { "Content-Type": "application/manifest+json" } });
}
