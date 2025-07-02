import { useState } from 'react'
import { ChevronDown } from 'lucide-react'

export default function Header() {
  const [showCategoryDropdown, setShowCategoryDropdown] = useState(false)

  const categoryOptions = [
    { label: 'Toutes les catégories', value: 'all' },
    { label: 'Actions & Fonds', value: 'stocks' },
    { label: 'Crypto', value: 'crypto' },
    { label: 'Immobilier', value: 'real-estate' },
    { label: 'Livrets', value: 'savings' },
  ]

  return (
    <header className="border-b border-border bg-background p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-white mb-1">Patrimoine brut</h1>
          <p className="text-sm text-muted">01 Jan. 2025</p>
        </div>
        
        <div className="flex items-center space-x-4">
          {/* Category Dropdown */}
          <div className="relative">
            <button
              onClick={() => setShowCategoryDropdown(!showCategoryDropdown)}
              className="flex items-center space-x-2 text-sm text-muted hover:text-white transition-colors"
            >
              <span>Toutes les catégories</span>
              <ChevronDown className="w-4 h-4" />
            </button>
            
            {showCategoryDropdown && (
              <div className="absolute right-0 top-full mt-2 w-48 bg-card border border-border rounded-lg shadow-lg z-10">
                {categoryOptions.map((option) => (
                  <button
                    key={option.value}
                    className="w-full text-left px-3 py-2 text-sm text-muted hover:text-white hover:bg-background transition-colors first:rounded-t-lg last:rounded-b-lg"
                    onClick={() => setShowCategoryDropdown(false)}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            )}
          </div>
          
          {/* Performance Section */}
          <div className="flex items-center space-x-2">
            <span className="text-sm text-muted">Performance</span>
            <ChevronDown className="w-4 h-4 text-muted" />
          </div>
        </div>
      </div>
    </header>
  )
}