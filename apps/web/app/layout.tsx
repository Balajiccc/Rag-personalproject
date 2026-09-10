export const metadata = {
  title: "AEGIS",
  description: "AEGIS — Day 1 scaffold",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
