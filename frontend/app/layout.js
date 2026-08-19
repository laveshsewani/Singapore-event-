import "./globals.css";

export const metadata = {
  title: "SG Tech Events — Founder Signal",
  description: "Tech events in Singapore, Aug–Oct, with flagged founder signals",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="font-body">{children}</body>
    </html>
  );
}
