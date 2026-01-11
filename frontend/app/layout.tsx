import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'IndexPulse - 指数ETF情报中心',
  description: '实时监控标普500、纳斯达克100、沪深300、科创50、恒生指数ETF的溢价率、资金流向和行情变动',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen bg-dark-bg text-dark-text">
        {children}
      </body>
    </html>
  )
}
