import { useState } from 'react'
import { 
  LayoutDashboard, 
  Wallet, 
  TrendingUp, 
  BarChart3,
  Calculator,
  ChevronDown,
  ChevronRight,
  Menu
} from 'lucide-react'

const menuItems = [
  { 
    id: 'synthese', 
    label: 'Synthèse', 
    icon: LayoutDashboard, 
    href: '/' 
  },
  {
    id: 'patrimoine',
    label: 'Patrimoine',
    icon: Wallet,
    submenu: [
      { id: 'livrets', label: 'Livrets', href: '/patrimoine/livrets' },
      { id: 'actions-fonds', label: 'Actions & Fonds', href: '/patrimoine/actions-fonds' },
      { id: 'fonds-euros', label: 'Fonds euros', href: '/patrimoine/fonds-euros' },
      { id: 'comptes-bancaires', label: 'Comptes bancaires', href: '/patrimoine/comptes-bancaires' },
      { id: 'crypto', label: 'Crypto', href: '/patrimoine/crypto' },
      { id: 'immobilier', label: 'Immobilier', href: '/patrimoine/immobilier' },
    ]
  },
  { 
    id: 'analyse', 
    label: 'Analyse', 
    icon: BarChart3, 
    href: '/analyse' 
  },
  { 
    id: 'budget', 
    label: 'Budget', 
    icon: Calculator, 
    href: '/budget' 
  },
  {
    id: 'outils',
    label: 'Outils',
    icon: TrendingUp,
    href: '/outils'
  }
]

export default function Sidebar({ collapsed, onToggle }) {
  const [expandedItems, setExpandedItems] = useState({})

  const toggleExpand = (itemId) => {
    setExpandedItems(prev => ({
      ...prev,
      [itemId]: !prev[itemId]
    }))
  }

  const renderMenuItem = (item) => {
    const hasSubmenu = item.submenu && item.submenu.length > 0
    const isExpanded = expandedItems[item.id]
    const Icon = item.icon

    return (
      <div key={item.id} className="mb-1">
        <div
          className={`flex items-center justify-between w-full p-3 text-left rounded-lg transition-colors hover:bg-background/50 cursor-pointer ${
            collapsed ? 'justify-center' : ''
          }`}
          onClick={() => hasSubmenu ? toggleExpand(item.id) : null}
        >
          <div className="flex items-center">
            <Icon className="w-5 h-5 text-muted" />
            {!collapsed && (
              <span className="ml-3 text-sm font-medium text-white">{item.label}</span>
            )}
          </div>
          {hasSubmenu && !collapsed && (
            <div className="text-muted">
              {isExpanded ? (
                <ChevronDown className="w-4 h-4" />
              ) : (
                <ChevronRight className="w-4 h-4" />
              )}
            </div>
          )}
        </div>
        
        {hasSubmenu && isExpanded && !collapsed && (
          <div className="ml-8 mt-1 space-y-1">
            {item.submenu.map((subItem) => (
              <div
                key={subItem.id}
                className="p-2 text-sm text-muted hover:text-white hover:bg-background/30 rounded-md cursor-pointer transition-colors"
              >
                {subItem.label}
              </div>
            ))}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className={`fixed left-0 top-0 h-full bg-card border-r border-border transition-all duration-300 z-50 ${
      collapsed ? 'w-16' : 'w-64'
    }`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border">
        {!collapsed && (
          <div className="flex items-center">
            <div className="w-8 h-8 bg-gradient-to-r from-orange-400 to-yellow-400 rounded-lg flex items-center justify-center">
              <span className="text-black font-bold text-sm">P</span>
            </div>
            <span className="ml-2 text-lg font-semibold">Patrimo</span>
          </div>
        )}
        <button
          onClick={onToggle}
          className="p-2 rounded-lg hover:bg-background transition-colors"
        >
          <Menu className="w-5 h-5" />
        </button>
      </div>

      {/* Navigation */}
      <nav className="p-4 space-y-2">
        {menuItems.map(renderMenuItem)}
      </nav>
    </div>
  )
}