import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Orion — Business development",
  description: "Local conversational prospect intelligence for Orion",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}