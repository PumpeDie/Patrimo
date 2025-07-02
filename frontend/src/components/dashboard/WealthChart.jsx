import { LineChart, Line, XAxis, YAxis, ResponsiveContainer } from 'recharts'
import Card from '../ui/Card'

// Sample data for the chart
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

export default function WealthChart() {
  return (
    <Card className="mb-6 h-96">
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
    </Card>
  )
}