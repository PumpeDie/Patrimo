import { useState, useEffect } from 'react'
import { useApi } from './useApi'

export function usePortfolio(period = 'ytd') {
  const { data: portfolioData, loading, error } = useApi(`/portfolio?period=${period}`)
  const [sortedAssets, setSortedAssets] = useState([])

  useEffect(() => {
    if (portfolioData?.assets) {
      // Sort assets by performance descending
      const sorted = [...portfolioData.assets].sort((a, b) => b.performance - a.performance)
      setSortedAssets(sorted)
    }
  }, [portfolioData])

  const totalValue = portfolioData?.totalValue || 0
  const totalPerformance = portfolioData?.totalPerformance || 0
  const performanceValue = portfolioData?.performanceValue || 0
  const historicalData = portfolioData?.historicalData || []

  return {
    assets: sortedAssets,
    totalValue,
    totalPerformance,
    performanceValue,
    historicalData,
    loading,
    error
  }
}