import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { fetchCatalog } from '../api/client'
import { ErrorMsg, Card, PageHeader, EmptyState } from '../components/ui'
import { Badge } from '../components/Badge'
import { SkeletonGrid } from '../components/Skeleton'

export function Catalog() {
  const { data, isLoading, error } = useQuery({ queryKey: ['catalog'], queryFn: fetchCatalog })
  const navigate = useNavigate()

  return (
    <div>
      <PageHeader title="Product Catalog" subtitle={data ? `Version ${data.version} · ${data.products.length} products` : 'Active catalog'} />
      {isLoading && <SkeletonGrid cards={6} variant="product" />}
      {error && <ErrorMsg msg="Failed to load catalog" />}
      {data && data.products.length === 0 && <EmptyState label="No products in catalog" />}
      {data && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {data.products.map(p => (
            <Card key={p.product_id} className="flex flex-col p-5">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-semibold text-slate-900">{p.name}</p>
                  <p className="mt-0.5 text-xs text-slate-500">{p.product_id}</p>
                </div>
                <Badge label={p.category} variant="blue" />
              </div>
              <p className="mt-3 text-sm text-slate-600 line-clamp-2">{p.description}</p>
              <div className="mt-4 grid grid-cols-2 gap-2 text-xs">
                <div className="rounded-lg bg-slate-50 p-2.5">
                  <p className="text-slate-400">Base Price</p>
                  <p className="mt-0.5 font-semibold text-slate-800">
                    {p.currency} {Number(p.base_price).toLocaleString('en-IN')}
                  </p>
                </div>
                <div className="rounded-lg bg-slate-50 p-2.5">
                  <p className="text-slate-400">Margin Floor</p>
                  <p className="mt-0.5 font-semibold text-slate-800">{(p.margin_floor * 100).toFixed(0)}%</p>
                </div>
                <div className="rounded-lg bg-slate-50 p-2.5">
                  <p className="text-slate-400">Inventory</p>
                  <p className="mt-0.5 font-semibold text-slate-800">{p.inventory} units</p>
                </div>
                <div className="rounded-lg bg-slate-50 p-2.5">
                  <p className="text-slate-400">Discount Rules</p>
                  <p className="mt-0.5 font-semibold text-slate-800">
                    {Object.keys(p.discount_rules).length > 0 ? 'Custom' : 'Default'}
                  </p>
                </div>
              </div>
              <button
                onClick={() => navigate('/buyer-simulator', { state: { product: p } })}
                className="mt-4 w-full rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
              >
                Buy
              </button>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
