export default function Card({ children, className = '' }) {
  return (
    <div className={`bg-card border border-border rounded-lg p-6 ${className}`}>
      {children}
    </div>
  )
}