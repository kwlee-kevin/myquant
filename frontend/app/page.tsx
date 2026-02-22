import Link from "next/link";

export default function HomePage() {
  return (
    <main className="mx-auto max-w-3xl p-8">
      <h1 className="text-2xl font-semibold">MyQuant-v2 Frontend</h1>
      <p className="mt-3 text-gray-700">
        Next.js 14 App Router scaffold for Stock Information Lookup System (KRX).
      </p>
      <Link
        href="/stocks"
        className="mt-6 inline-block rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
      >
        Go to Stocks
      </Link>
    </main>
  );
}
