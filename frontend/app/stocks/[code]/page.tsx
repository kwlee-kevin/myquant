import Link from "next/link";

type StockDetail = {
  code: string;
  name_kr: string;
  name_en: string | null;
  market: string;
  security_type: string;
  mrkt_tp_raw: string | null;
  market_code_raw: string | null;
  category_l1: string | null;
  category_l2: string | null;
  is_active: boolean;
  listed_date: string | null;
  delisted_date: string | null;
  created_at: string;
  updated_at: string;
};

type Props = {
  params: { code: string };
};

export default async function StockDetailPage({ params }: Props) {
  const base = process.env.NEXT_PUBLIC_API_BASE ?? "http://backend:8000";
  const url = `${base}/api/stocks/${params.code}`;

  let data: StockDetail | null = null;
  let error = "";
  let notFound = false;

  try {
    const res = await fetch(url, {
      cache: "no-store",
      headers: { Accept: "application/json" },
    });

    if (res.status === 404) {
      notFound = true;
    } else if (!res.ok) {
      error = `Failed to load stock detail (status=${res.status}).`;
    } else {
      data = (await res.json()) as StockDetail;
    }
  } catch {
    error = "Failed to load stock detail (network/server error).";
  }

  return (
    <main className="mx-auto max-w-3xl p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Stock Detail</h1>
        <Link href="/stocks" className="text-sm text-blue-600 hover:underline">
          Back to Stocks
        </Link>
      </div>

      {notFound ? <p className="text-gray-700">Not found: stock code {params.code}</p> : null}
      {!notFound && error ? <p className="text-red-600">{error}</p> : null}

      {!notFound && !error && data ? (
        <div className="rounded border border-gray-200 p-4">
          <dl className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div>
              <dt className="text-xs text-gray-500">code</dt>
              <dd>{data.code}</dd>
            </div>
            <div>
              <dt className="text-xs text-gray-500">name_kr</dt>
              <dd>{data.name_kr}</dd>
            </div>
            <div>
              <dt className="text-xs text-gray-500">name_en</dt>
              <dd>{data.name_en ?? "-"}</dd>
            </div>
            <div>
              <dt className="text-xs text-gray-500">market</dt>
              <dd>{data.market}</dd>
            </div>
            <div>
              <dt className="text-xs text-gray-500">security_type</dt>
              <dd>{data.security_type}</dd>
            </div>
            <div>
              <dt className="text-xs text-gray-500">mrkt_tp_raw</dt>
              <dd>{data.mrkt_tp_raw ?? "-"}</dd>
            </div>
            <div>
              <dt className="text-xs text-gray-500">market_code_raw</dt>
              <dd>{data.market_code_raw ?? "-"}</dd>
            </div>
            <div>
              <dt className="text-xs text-gray-500">category_l1</dt>
              <dd>{data.category_l1 ?? "-"}</dd>
            </div>
            <div>
              <dt className="text-xs text-gray-500">category_l2</dt>
              <dd>{data.category_l2 ?? "-"}</dd>
            </div>
            <div>
              <dt className="text-xs text-gray-500">is_active</dt>
              <dd>{String(data.is_active)}</dd>
            </div>
            <div>
              <dt className="text-xs text-gray-500">listed_date</dt>
              <dd>{data.listed_date ?? "-"}</dd>
            </div>
            <div>
              <dt className="text-xs text-gray-500">updated_at</dt>
              <dd>{new Date(data.updated_at).toLocaleString()}</dd>
            </div>
          </dl>
        </div>
      ) : null}
    </main>
  );
}
