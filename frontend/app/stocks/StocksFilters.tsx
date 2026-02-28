"use client";

import { FormEvent, useMemo, useState } from "react";
import { usePathname, useRouter } from "next/navigation";

import { buildQuery } from "@/lib/api";

type StocksFiltersProps = {
  initialKeywords: string;
  initialOp: "and" | "or";
  initialMarkets: string[];
  initialSecurityTypes: string[];
  initialCategories: string[];
  initialPageSize: number;
  stats: {
    by_market: Record<string, number>;
    top_category_l1: Array<{ category_l1: string; count: number }>;
  } | null;
};

const MARKET_OPTIONS = ["KOSPI", "KOSDAQ", "KONEX"];
const SECURITY_TYPE_OPTIONS = [
  "COMMON_STOCK",
  "ETF",
  "ETN",
  "ETN_LOSS_LIMIT",
  "GOLD_SPOT",
  "ETN_VOLATILITY",
  "INFRA_FUND",
  "ELW",
  "MUTUAL_FUND",
  "WARRANT",
  "REIT",
  "WARRANT_CERT",
  "HIGH_YIELD_FUND",
];

export default function StocksFilters({
  initialKeywords,
  initialOp,
  initialMarkets,
  initialSecurityTypes,
  initialCategories,
  initialPageSize,
  stats,
}: StocksFiltersProps) {
  const router = useRouter();
  const pathname = usePathname();

  const [keywords, setKeywords] = useState(initialKeywords);
  const [op, setOp] = useState<"and" | "or">(initialOp);
  const [markets, setMarkets] = useState<string[]>(initialMarkets);
  const [securityTypes, setSecurityTypes] = useState<string[]>(initialSecurityTypes);
  const [categories, setCategories] = useState<string[]>(initialCategories);
  const [pageSize, setPageSize] = useState<number>(initialPageSize);

  const selectedMarketSet = useMemo(() => new Set(markets), [markets]);
  const selectedSecurityTypeSet = useMemo(() => new Set(securityTypes), [securityTypes]);
  const selectedCategorySet = useMemo(() => new Set(categories), [categories]);

  const pushFilters = (next: {
    keywords: string;
    op: "and" | "or";
    markets: string[];
    securityTypes: string[];
    categories: string[];
    pageSize: number;
  }) => {
    const query = buildQuery({
      keywords: next.keywords,
      op: next.op,
      markets: next.markets,
      security_types: next.securityTypes,
      categories: next.categories,
      page: 1,
      page_size: next.pageSize,
    });
    router.push(`${pathname}${query}`);
  };

  const onSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    pushFilters({ keywords, op, markets, securityTypes, categories, pageSize });
  };

  const toggleMarket = (market: string) => {
    const nextMarkets = selectedMarketSet.has(market)
      ? markets.filter((value) => value !== market)
      : [...markets, market];
    setMarkets(nextMarkets);
    pushFilters({ keywords, op, markets: nextMarkets, securityTypes, categories, pageSize });
  };

  const toggleSecurityType = (securityType: string) => {
    const nextSecurityTypes = selectedSecurityTypeSet.has(securityType)
      ? securityTypes.filter((value) => value !== securityType)
      : [...securityTypes, securityType];
    setSecurityTypes(nextSecurityTypes);
    pushFilters({
      keywords,
      op,
      markets,
      securityTypes: nextSecurityTypes,
      categories,
      pageSize,
    });
  };

  const toggleCategory = (category: string) => {
    const nextCategories = selectedCategorySet.has(category)
      ? categories.filter((value) => value !== category)
      : [...categories, category];
    setCategories(nextCategories);
    pushFilters({
      keywords,
      op,
      markets,
      securityTypes,
      categories: nextCategories,
      pageSize,
    });
  };

  return (
    <form onSubmit={onSubmit} className="mb-5 rounded border border-gray-200 p-4">
      <div className="grid gap-4 md:grid-cols-2">
        <label className="block">
          <span className="mb-1 block text-sm font-medium">Keywords</span>
          <input
            value={keywords}
            onChange={(e) => setKeywords(e.target.value)}
            placeholder="예: 삼성"
            className="w-full rounded border border-gray-300 px-3 py-2"
          />
        </label>

        <label className="block">
          <span className="mb-1 block text-sm font-medium">Operator</span>
          <select
            value={op}
            onChange={(e) => {
              const nextOp = e.target.value as "and" | "or";
              setOp(nextOp);
              pushFilters({ keywords, op: nextOp, markets, securityTypes, categories, pageSize });
            }}
            className="w-full rounded border border-gray-300 px-3 py-2"
          >
            <option value="and">AND</option>
            <option value="or">OR</option>
          </select>
        </label>
      </div>

      <div className="mt-4">
        <p className="mb-1 text-sm font-medium">Markets</p>
        <div className="flex flex-wrap gap-3">
          {MARKET_OPTIONS.map((market) => {
            const count = stats?.by_market?.[market];
            return (
              <label key={market} className="inline-flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={selectedMarketSet.has(market)}
                  onChange={() => toggleMarket(market)}
                />
                <span>
                  {market}
                  {typeof count === "number" ? ` (${count})` : ""}
                </span>
              </label>
            );
          })}
        </div>
      </div>

      <div className="mt-4">
        <p className="mb-1 text-sm font-medium">Security Types</p>
        <div className="flex flex-wrap gap-3">
          {SECURITY_TYPE_OPTIONS.map((securityType) => (
            <label key={securityType} className="inline-flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={selectedSecurityTypeSet.has(securityType)}
                onChange={() => toggleSecurityType(securityType)}
              />
              <span>{securityType}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="mt-4">
        <p className="mb-1 text-sm font-medium">Top Categories</p>
        {stats?.top_category_l1?.length ? (
          <div className="flex flex-wrap gap-3">
            {stats.top_category_l1.map((item) => (
              <label key={item.category_l1} className="inline-flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={selectedCategorySet.has(item.category_l1)}
                  onChange={() => toggleCategory(item.category_l1)}
                />
                <span>
                  {item.category_l1} ({item.count})
                </span>
              </label>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-500">Category stats unavailable.</p>
        )}
      </div>

      <div className="mt-4 flex items-end justify-between">
        <label className="block w-44">
          <span className="mb-1 block text-sm font-medium">Page Size</span>
          <select
            value={pageSize}
            onChange={(e) => {
              const nextSize = Number(e.target.value);
              setPageSize(nextSize);
              pushFilters({
                keywords,
                op,
                markets,
                securityTypes,
                categories,
                pageSize: nextSize,
              });
            }}
            className="w-full rounded border border-gray-300 px-3 py-2"
          >
            <option value={20}>20</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
          </select>
        </label>

        <button
          type="submit"
          className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        >
          Search
        </button>
      </div>
    </form>
  );
}
