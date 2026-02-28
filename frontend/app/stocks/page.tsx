import Link from "next/link";

import { buildQuery } from "@/lib/api";

import StocksFilters from "./StocksFilters";

type StockRow = {
  code: string;
  name_kr: string;
  market: string;
  security_type: string;
  category_l1: string | null;
  updated_at: string;
};

type StocksResponse = {
  count: number;
  page: number;
  page_size: number;
  results: StockRow[];
};

type StocksStats = {
  by_market: Record<string, number>;
  top_category_l1: Array<{ category_l1: string; count: number }>;
};

type StocksPageProps = {
  searchParams?: {
    keywords?: string;
    op?: string;
    markets?: string | string[];
    security_types?: string | string[];
    categories?: string | string[];
    page?: string;
    page_size?: string;
  };
};

function normalizeList(value: string | string[] | undefined): string[] {
  if (!value) {
    return [];
  }
  return Array.isArray(value) ? value.filter(Boolean) : [value];
}

function clampPageSize(value: string | undefined): number {
  const parsed = Number(value ?? "20");
  if (parsed === 50 || parsed === 100) {
    return parsed;
  }
  return 20;
}

function parsePage(value: string | undefined): number {
  const parsed = Number(value ?? "1");
  return Number.isFinite(parsed) && parsed > 0 ? Math.floor(parsed) : 1;
}

export default async function StocksPage({ searchParams }: StocksPageProps) {
  const keywords = searchParams?.keywords ?? "";
  const op = searchParams?.op === "or" ? "or" : "and";
  const markets = normalizeList(searchParams?.markets);
  const securityTypes = normalizeList(searchParams?.security_types);
  const categories = normalizeList(searchParams?.categories);
  const pageSize = clampPageSize(searchParams?.page_size);
  const page = parsePage(searchParams?.page);

  const internalBase = process.env.NEXT_PUBLIC_API_BASE ?? "http://backend:8000";

  const listQuery = buildQuery({
    keywords,
    op,
    markets,
    security_types: securityTypes,
    categories,
    page,
    page_size: pageSize,
  });
  const listUrl = `${internalBase}/api/stocks${listQuery}`;

  let data: StocksResponse | null = null;
  let error = "";
  let stats: StocksStats | null = null;

  try {
    const response = await fetch(listUrl, {
      cache: "no-store",
      headers: { Accept: "application/json" },
    });
    if (!response.ok) {
      throw new Error(`status=${response.status} url=${listUrl}`);
    }
    data = (await response.json()) as StocksResponse;
  } catch (err) {
    const message = err instanceof Error ? err.message : "unknown error";
    error = `Server fetch failed (${message}).`;
  }

  try {
    const statsRes = await fetch(`${internalBase}/api/stocks/stats`, {
      cache: "no-store",
      headers: { Accept: "application/json" },
    });
    if (statsRes.ok) {
      stats = (await statsRes.json()) as StocksStats;
    }
  } catch {
    stats = null;
  }

  const totalPages =
    data && data.page_size > 0 ? Math.max(1, Math.ceil(data.count / data.page_size)) : 1;

  const prevQuery = buildQuery({
    keywords,
    op,
    markets,
    security_types: securityTypes,
    categories,
    page: Math.max(1, page - 1),
    page_size: pageSize,
  });
  const nextQuery = buildQuery({
    keywords,
    op,
    markets,
    security_types: securityTypes,
    categories,
    page: Math.min(totalPages, page + 1),
    page_size: pageSize,
  });

  return (
    <main className="mx-auto max-w-7xl p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Stocks</h1>
        <Link href="/" className="text-sm text-blue-600 hover:underline">
          Back Home
        </Link>
      </div>

      <p className="mb-2 text-xs text-gray-500">Internal API base (server): {internalBase}</p>

      <StocksFilters
        initialKeywords={keywords}
        initialOp={op}
        initialMarkets={markets}
        initialSecurityTypes={securityTypes}
        initialCategories={categories}
        initialPageSize={pageSize}
        stats={stats}
      />

      {error ? <p className="text-red-600">{error}</p> : null}

      {!error && data ? (
        <>
          <div className="overflow-x-auto rounded border border-gray-200">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 py-2 text-left">name_kr</th>
                  <th className="px-3 py-2 text-left">code</th>
                  <th className="px-3 py-2 text-left">market</th>
                  <th className="px-3 py-2 text-left">security_type</th>
                  <th className="px-3 py-2 text-left">category_l1</th>
                  <th className="px-3 py-2 text-left">updated_at</th>
                </tr>
              </thead>
              <tbody>
                {data.results.map((row) => (
                  <tr key={row.code} className="border-t">
                    <td className="px-3 py-2">
                      <Link href={`/stocks/${row.code}`} className="text-blue-600 hover:underline">
                        {row.name_kr}
                      </Link>
                    </td>
                    <td className="px-3 py-2">{row.code}</td>
                    <td className="px-3 py-2">{row.market}</td>
                    <td className="px-3 py-2">{row.security_type}</td>
                    <td className="px-3 py-2">{row.category_l1 ?? "-"}</td>
                    <td className="px-3 py-2">{new Date(row.updated_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-4 flex items-center justify-between">
            <p className="text-sm text-gray-600">
              Page {data.page} / {totalPages} · Total {data.count}
            </p>
            <div className="flex gap-2">
              {page > 1 ? (
                <Link
                  href={`/stocks${prevQuery}`}
                  className="rounded border border-gray-300 px-3 py-1"
                >
                  Prev
                </Link>
              ) : (
                <span className="rounded border border-gray-200 px-3 py-1 text-gray-400">Prev</span>
              )}
              {page < totalPages ? (
                <Link
                  href={`/stocks${nextQuery}`}
                  className="rounded border border-gray-300 px-3 py-1"
                >
                  Next
                </Link>
              ) : (
                <span className="rounded border border-gray-200 px-3 py-1 text-gray-400">Next</span>
              )}
            </div>
          </div>
        </>
      ) : null}
    </main>
  );
}
