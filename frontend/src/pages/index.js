import Head from 'next/head'
import WealthSummary from '../components/dashboard/WealthSummary'
import PerformanceGrid from '../components/dashboard/PerformanceGrid'

export default function Home() {
  return (
    <>
      <Head>
        <title>Dashboard | Patrimo</title>
      </Head>
      <div className="space-y-6">
        <WealthSummary />
        <PerformanceGrid />
      </div>
    </>
  )
}