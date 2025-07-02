import { TrendingUp, TrendingDown } from 'lucide-react'

export default function AssetCard({ asset }) {
  const isPositive = asset.performance >= 0
  
  return (
    <div className="bg-card border border-border rounded-lg p-4 hover:bg-card/80 transition-colors">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-3">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium ${asset.bgColor}`}>
            {asset.symbol}
          </div>
          <div>
            <h3 className="font-medium text-white text-sm">{asset.name}</h3>
            <p className="text-xs text-muted">{asset.code}</p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-sm font-medium text-white">{asset.value} €</div>
          <div className={`flex items-center text-xs ${isPositive ? 'text-accent' : 'text-destructive'}`}>
            {isPositive ? (
              <TrendingUp className="w-3 h-3 mr-1" />
            ) : (
              <TrendingDown className="w-3 h-3 mr-1" />
            )}
            {isPositive ? '+' : ''}{asset.performance}%
          </div>
        </div>
      </div>
      
      {/* Mini chart placeholder */}
      <div className="h-12 bg-background rounded flex items-end justify-between px-1">
        {Array.from({ length: 20 }, (_, i) => (
          <div
            key={i}
            className={`w-1 rounded-t ${isPositive ? 'bg-accent' : 'bg-destructive'}`}
            style={{ 
              height: `${Math.random() * 100}%`,
              opacity: 0.7 
            }}
          />
        ))}
      </div>
    </div>
  )
}