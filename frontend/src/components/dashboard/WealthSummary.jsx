import { useState } from 'react'
import { ChevronDown } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer } from 'recharts'
import Card from '../ui/Card'
import PerformanceCard from './PerformanceCard'
import { usePortfolio } from '../../hooks/usePortfolio'

// Sample chart data - should come from API
const chartData = [
  { date: '10/01/2025', value: 77100 },
  { date: '13/01/2025', value: 82500 },
  { date: '23/01/2025', value: 88100 },
  { date: '31/01/2025', value: 93500 },
  { date: '08/04/2025', value: 99100 },
  { date: '15/04/2025', value: 96800 },
  { date: '16/04/2025', value: 94200 },
  { date: '16/04/2025', value: 97431 },
]

export default function WealthSummary() {
  const [selectedPeriod, setSelectedPeriod] = useState('ytd')
  const [showTypeDropdown, setShowTypeDropdown] = useState(false)
  const [patrimoineType, setPatrimoineType] = useState('brut')
  
  const { totalValue, historicalData, loading } = usePortfolio(selectedPeriod)

  const timeOptions = [
    { label: '1J', value: '1d' },
    { label: '7J', value: '7d' },
    { label: '1M', value: '1m' },
    { label: 'YTD', value: 'ytd' },
    { label: 'TOUT', value: 'all' }
  ]

  const patrimoineTypes = [
    { label: 'Patrimoine brut', value: 'brut' },
    { label: 'Patrimoine net', value: 'net' },
    { label: 'Patrimoine financier', value: 'financier' }
  ]

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)
  }

  const formatCompactCurrency = (value) => {
    if (value >= 1000) {
      return `${(value / 1000).toFixed(1)} k€`
    }
    return formatCurrency(value)
  }

  // Get the last 5 data points for historical display
  const recentValues = historicalData?.slice(-5) || []

  if (loading) {
    return (
      <div className="grid grid-cols-3 gap-6 mb-6">
        <Card className="col-span-2">
          <div className="animate-pulse">
            <div className="flex items-center justify-between mb-4">
              <div className="h-6 bg-border rounded w-48"></div>
              <div className="flex space-x-2">
                {Array.from({ length: 5 }, (_, i) => (
                  <div key={i} className="h-8 bg-border rounded w-12"></div>
                ))}
              </div>
            </div>
            <div className="h-4 bg-border rounded w-24 mb-4"></div>
            <div className="h-12 bg-border rounded w-48 mb-2"></div>
            <div className="h-64 bg-border rounded"></div>
          </div>
        </Card>
        <Card>
          <div className="animate-pulse">
            <div className="h-6 bg-border rounded w-24 mb-4"></div>
            <div className="h-32 bg-border rounded"></div>
          </div>
        </Card>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-3 gap-6 mb-6">
      {/* Main Wealth Card with Chart - 2/3 width */}
      <Card className="col-span-2">
        {/* Header with title and period buttons */}
        <div className="flex items-center justify-between mb-6">
          {/* Patrimoine Type Dropdown */}
          <div className="relative">
            <button
              onClick={() => setShowTypeDropdown(!showTypeDropdown)}
              className="flex items-center space-x-2 text-lg font-semibold text-white hover:text-muted transition-colors"
            >
              <span>{patrimoineTypes.find(t => t.value === patrimoineType)?.label}</span>
              <ChevronDown className="w-4 h-4" />
            </button>
            
            {showTypeDropdown && (
              <div className="absolute left-0 top-full mt-2 w-48 bg-card border border-border rounded-lg shadow-lg z-10">
                {patrimoineTypes.map((type) => (
                  <button
                    key={type.value}
                    className={`w-full text-left px-3 py-2 text-sm transition-colors first:rounded-t-lg last:rounded-b-lg ${
                      patrimoineType === type.value 
                        ? 'text-primary bg-primary/10' 
                        : 'text-muted hover:text-white hover:bg-background'
                    }`}
                    onClick={() => {
                      setPatrimoineType(type.value)
                      setShowTypeDropdown(false)
                    }}
                  >
                    {type.label}
                    {patrimoineType === type.value && (
                      <span className="ml-2 text-primary">✓</span>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Time Period Buttons */}
          <div className="flex bg-background border border-border rounded-lg p-1">
            {timeOptions.map((option) => (
              <button
                key={option.value}
                onClick={() => setSelectedPeriod(option.value)}
                className={`px-3 py-1 text-xs font-medium rounded transition-colors ${
                  selectedPeriod === option.value
                    ? 'bg-primary text-white' 
                    : 'text-muted hover:text-white hover:bg-card'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        {/* Date */}
        <p className="text-sm text-muted mb-4">01 Jan. 2025</p>

        {/* Main value and historical data */}
        <div className="mb-6">
          <h2 className="text-4xl font-bold text-white mb-2">
            {formatCurrency(totalValue)}
          </h2>
          {recentValues.length > 0 && (
            <div className="flex items-center space-x-4 text-sm text-muted">
              {recentValues.map((dataPoint, index) => (
                <span key={index}>
                  {formatCompactCurrency(dataPoint.value)}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Integrated Chart */}
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <XAxis 
                dataKey="date" 
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12, fill: '#6b7280' }}
              />
              <YAxis hide />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke="#d97706" 
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4, fill: '#d97706' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Right Card - 1/3 width */}
      <PerformanceCard selectedPeriod={selectedPeriod} />
    </div>
  )
}