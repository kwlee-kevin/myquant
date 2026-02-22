import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "MyQuant-v2",
  description: "Stock Information Lookup System (KRX)",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
