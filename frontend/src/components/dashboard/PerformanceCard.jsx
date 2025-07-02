import { useState } from 'react'
import { ChevronDown } from 'lucide-react'
import Card from '../ui/Card'
import { usePortfolio } from '../../hooks/usePortfolio'

export default function PerformanceCard({ selectedPeriod }) {
  const [showTypeDropdown, setShowTypeDropdown] = useState(false)
  const [cardType, setCardType] = useState('performance')
  const [viewType, setViewType] = useState('treemap')
  
  const { totalPerformance, performanceValue, assets, totalValue, loading } = usePortfolio(selectedPeriod)

  const cardTypes = [
    { label: 'Performance', value: 'performance' },
    { label: 'Allocation', value: 'allocation' }
  ]

  // Allocation colors management
  const getAllocationColor = (index) => {
    const colors = [
      'bg-blue-500', 'bg-green-500', 'bg-yellow-500', 'bg-purple-500',
      'bg-red-500', 'bg-indigo-500', 'bg-pink-500', 'bg-orange-500'
    ]
    return colors[index % colors.length]
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)
  }

  const formatPerformance = (value) => {
    const sign = value >= 0 ? '+' : ''
    return `${sign}${value.toFixed(2)} %`
  }

  // Calculate allocation data
  const allocationData = assets.map(asset => ({
    name: asset.category,
    shortName: asset.categoryShort || asset.category?.substring(0, 8),
    value: asset.value,
    percentage: ((asset.value / totalValue) * 100).toFixed(1),
  }))

  // Group by category and sum values
  const groupedAllocation = allocationData.reduce((acc, item) => {
    const existingCategory = acc.find(cat => cat.name === item.name)
    if (existingCategory) {
      existingCategory.value += item.value
      existingCategory.percentage = ((existingCategory.value / totalValue) * 100).toFixed(1)
    } else {
      acc.push({ ...item })
    }
    return acc
  }, [])

  // Sort by value (descending) and assign colors based on ranking
  const sortedAllocation = groupedAllocation
    .sort((a, b) => b.value - a.value)
    .map((item, index) => ({
      ...item,
      color: getAllocationColor(index)
    }))

  const TreemapView = () => {
    return (
      <div className="space-y-3">
        {sortedAllocation.map((item, index) => (
          <div key={index} className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className={`w-3 h-3 rounded ${item.color}`}></div>
              <span className="text-sm text-white">{item.shortName}</span>
            </div>
            <div className="text-right">
              <div className="text-sm font-medium text-white">{item.percentage}%</div>
              <div className="text-xs text-muted">{formatCurrency(item.value)}</div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  const PieChartView = () => (
    <div className="h-64 flex items-center justify-center">
      <div className="w-48 h-48 relative">
        <svg viewBox="0 0 100 100" className="w-full h-full transform -rotate-90">
          {sortedAllocation.reduce((acc, item, index) => {
            const percentage = parseFloat(item.percentage)
            const strokeLength = (percentage / 100) * 283 // 2 * π * 45
            const strokeOffset = acc.offset
            
            const color = item.color.replace('bg-', '').replace('-500', '')
            const colorMap = {
              'blue': '#3b82f6',
              'green': '#10b981',
              'yellow': '#f59e0b',
              'purple': '#8b5cf6',
              'red': '#ef4444',
              'indigo': '#6366f1',
              'pink': '#ec4899',
              'orange': '#f97316'
            }
            
            acc.elements.push(
              <circle
                key={index}
                cx="50"
                cy="50"
                r="45"
                fill="none"
                stroke={colorMap[color] || '#3b82f6'}
                strokeWidth="10"
                strokeDasharray={`${strokeLength} 283`}
                strokeDashoffset={-strokeOffset}
                className="transition-all duration-300"
              />
            )
            
            acc.offset += strokeLength
            return acc
          }, { elements: [], offset: 0 }).elements}
        </svg>
        
        <div className="absolute inset-0 flex flex-col items-center justify-center text-white">
          <div className="text-lg font-bold">100%</div>
          <div className="text-xs text-muted">Total</div>
        </div>
      </div>
    </div>
  )

  const PerformanceContent = () => (
    <>
      <div className="mb-4">
        <div className="text-sm text-muted mb-1">Plus-value • Année en cours</div>
        <div className={`text-2xl font-bold ${totalPerformance >= 0 ? 'text-accent' : 'text-destructive'}`}>
          {totalPerformance >= 0 ? '+' : ''}{formatCurrency(performanceValue)}
        </div>
        <div className={`text-sm ${totalPerformance >= 0 ? 'text-accent' : 'text-destructive'}`}>
          {formatPerformance(totalPerformance)}
        </div>
      </div>

      <p className="text-xs text-muted mb-4">
        La plus-value latente est la variation de votre performance sur la période 
        sélectionnée. Ce montant ne tient pas compte des plus-values réalisées.
      </p>

      <button className="text-xs text-primary hover:underline">
        En savoir plus →
      </button>
    </>
  )

  const AllocationContent = () => (
    <>
      <div className="mb-4">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm text-muted">Vue</span>
          <div className="flex bg-background border border-border rounded p-1">
            <button
              onClick={() => setViewType('treemap')}
              className={`px-2 py-1 text-xs rounded transition-colors ${
                viewType === 'treemap' 
                  ? 'bg-primary text-white' 
                  : 'text-muted hover:text-white'
              }`}
            >
              Liste
            </button>
            <button
              onClick={() => setViewType('pie')}
              className={`px-2 py-1 text-xs rounded transition-colors ${
                viewType === 'pie' 
                  ? 'bg-primary text-white' 
                  : 'text-muted hover:text-white'
              }`}
            >
              Graphique
            </button>
          </div>
        </div>
        
        {viewType === 'treemap' ? <TreemapView /> : <PieChartView />}
      </div>
    </>
  )

  if (loading) {
    return (
      <Card>
        <div className="animate-pulse">
          <div className="h-6 bg-border rounded w-24 mb-4"></div>
          <div className="h-32 bg-border rounded"></div>
        </div>
      </Card>
    )
  }

  return (
    <Card>
      {/* Dropdown Header */}
      <div className="relative mb-4">
        <button
          onClick={() => setShowTypeDropdown(!showTypeDropdown)}
          className="flex items-center justify-between w-full text-left"
        >
          <span className="text-lg font-semibold text-white">
            {cardTypes.find(t => t.value === cardType)?.label}
          </span>
          <ChevronDown className="w-4 h-4 text-muted" />
        </button>
        
        {showTypeDropdown && (
          <div className="absolute left-0 top-full mt-2 w-full bg-card border border-border rounded-lg shadow-lg z-10">
            {cardTypes.map((type) => (
              <button
                key={type.value}
                className={`w-full text-left px-3 py-2 text-sm transition-colors first:rounded-t-lg last:rounded-b-lg ${
                  cardType === type.value 
                    ? 'text-primary bg-primary/10' 
                    : 'text-muted hover:text-white hover:bg-background'
                }`}
                onClick={() => {
                  setCardType(type.value)
                  setShowTypeDropdown(false)
                }}
              >
                {type.label}
                {cardType === type.value && (
                  <span className="ml-2 text-primary">✓</span>
                )}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Content based on card type */}
      {cardType === 'performance' ? <PerformanceContent /> : <AllocationContent />}
    </Card>
  )
}