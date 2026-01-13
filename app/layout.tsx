import type { Metadata } from "next";
import { Analytics } from "@vercel/analytics/react";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL('https://vacuumpartshub.com'),
  title: "VacuumPartsHub",
  description: "AI-Powered Vacuum Repair Guide & Parts Locator",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-gray-50">
        {children}
        <Analytics />
      </body>
    </html>
  );
}
