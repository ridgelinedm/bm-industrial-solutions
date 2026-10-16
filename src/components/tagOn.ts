// Which tag variant reads correctly on each coloured surface.
const TAG_ON: Record<string, string> = { ink: "onink", photo: "onink", red: "onred" };
export const tagVariant = (surface: string) => TAG_ON[surface] ?? "red";
