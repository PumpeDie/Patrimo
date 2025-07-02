import { useState } from 'react'
import { ChevronDown } from 'lucide-react'
import AssetCard from './AssetCard'
import { usePortfolio } from '../../hooks/usePortfolio'

const CATEGORY_OPTIONS = [
  { label: 'Toutes les catégories', value: 'all' },
  { label: 'Actions & Fonds', value: 'stocks' },
  { label: 'Crypto', value: 'crypto' },
  { label: 'Immobilier', value: 'real-estate' },
  { label: 'Livrets', value: 'savings' },
]

const SORT_OPTIONS = [
  { label: 'Performance', value: 'performance' },
  { label: 'Valeur', value: 'value' },
  { label: 'Nom', value: 'name' },
]

export default function PerformanceGrid() {
  const { assets, loading, error } = usePortfolio()
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [selectedSort, setSelectedSort] = useState('performance')

  // Filter assets by category
  const filteredAssets = assets.filter(asset => {
    if (selectedCategory === 'all') return true
    return asset.category === selectedCategory
  })

  // Sort assets
  const sortedAssets = [...filteredAssets].sort((a, b) => {
    switch (selectedSort) {
      case 'performance':
        return b.performance - a.performance
      case 'value':
        return b.value - a.value
      case 'name':
        return a.name.localeCompare(b.name)
      default:
        return 0
    }
  })

  if (loading) {
    return (
      <div className="mb-6">
        <div className="animate-pulse space-y-4">
          <div className="flex items-center justify-between">
            <div className="h-6 bg-border rounded w-1/4"></div>
            <div className="flex space-x-4">
              <div className="h-8 bg-border rounded w-32"></div>
              <div className="h-8 bg-border rounded w-24"></div>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {Array.from({ length: 8 }, (_, i) => (
              <div key={i} className="h-32 bg-border rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="mb-6">
        <div className="text-center py-8">
          <p className="text-destructive mb-2">Erreur lors du chargement des données</p>
          <p className="text-muted text-sm">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="mb-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-white">Ma performance</h2>
        
        <div className="flex items-center space-x-4">
          {/* Category Filter */}
          <div className="relative">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="appearance-none bg-card border border-border rounded px-3 py-1 text-sm text-muted pr-8 focus:outline-none focus:ring-2 focus:ring-primary"
            >
              {CATEGORY_OPTIONS.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted pointer-events-none" />
          </div>

          {/* Sort Filter */}
          <div className="relative">
            <select
              value={selectedSort}
              onChange={(e) => setSelectedSort(e.target.value)}
              className="appearance-none bg-card border border-border rounded px-3 py-1 text-sm text-muted pr-8 focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="" disabled>Trier par</option>
              {SORT_OPTIONS.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted pointer-events-none" />
          </div>
        </div>
      </div>
      
      {/* Assets Grid */}
      {sortedAssets.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-muted">Aucun actif trouvé pour cette catégorie</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-6 gap-4">
          {sortedAssets.map((asset) => (
            <AssetCard key={asset.id} asset={asset} />
          ))}
        </div>
      )}
    </div>
  )
}