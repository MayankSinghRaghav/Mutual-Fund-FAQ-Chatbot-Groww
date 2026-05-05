import ChatWidget from '@/components/ChatWidget';

export default function Home() {
  return (
    <div className="min-h-screen bg-[#f4f7fb] text-[#44475b]">
      {/* Groww Header */}
      <header className="bg-white border-bottom border-gray-200 px-8 py-3 flex items-center gap-12 sticky top-0 z-40">
        <div className="flex items-center gap-2 font-bold text-xl text-[#44475b]">
          <div className="w-8 h-8 bg-gradient-to-br from-[#00d09c] to-[#00b386] rounded-full"></div>
          Groww
        </div>
        <nav className="flex gap-8 font-medium text-sm">
          <a href="#" className="hover:text-[#00d09c]">Stocks</a>
          <a href="#" className="hover:text-[#00d09c]">F&O</a>
          <a href="#" className="text-[#00d09c] border-b-2 border-[#00d09c] pb-3 -mb-3">Mutual Funds</a>
        </nav>
      </header>

      {/* Ticker */}
      <div className="bg-white border-b border-gray-200 px-8 py-2 flex gap-8 overflow-x-auto text-xs whitespace-nowrap scrollbar-hide">
        <div className="flex flex-col"><span className="text-gray-400">NIFTY 50</span><span className="font-bold text-red-500">24,052.70 ▼ 66.60 (0.28%)</span></div>
        <div className="flex flex-col"><span className="text-gray-400">SENSEX</span><span className="font-bold text-red-500">77,065.59 ▼ 203.81 (0.26%)</span></div>
        <div className="flex flex-col"><span className="text-gray-400">BANKNIFTY</span><span className="font-bold text-red-500">54,815.95 ▼ 62.55 (0.11%)</span></div>
        <div className="flex flex-col"><span className="text-gray-400">MIDCPNIFTY</span><span className="font-bold text-[#00d09c]">13,953.95 ▲ 23.75 (0.17%)</span></div>
      </div>

      <main className="max-w-6xl mx-auto p-8 grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Left: Main Dashboard */}
        <div className="md:col-span-2 space-y-8">
          <section>
            <h2 className="text-lg font-bold mb-4">Most bought stocks on Groww</h2>
            <div className="grid grid-cols-3 gap-4">
              {[
                { name: 'Titagarh Rail', price: '₹855.40', chg: '+11.17%' },
                { name: 'PNB', price: '₹109.25', chg: '+0.52%' },
                { name: 'Vedanta', price: '₹302.30', chg: '+2.60%' }
              ].map((stock, i) => (
                <div key={i} className="bg-white p-5 rounded-lg border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
                  <div className="font-bold mb-2">{stock.name}</div>
                  <div className="text-lg font-medium">{stock.price}</div>
                  <div className="text-[#00d09c] text-sm font-bold">{stock.chg}</div>
                </div>
              ))}
            </div>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-4">Top movers today</h2>
            <div className="bg-white rounded-lg border border-gray-100 overflow-hidden shadow-sm">
              <div className="grid grid-cols-2 p-4 border-b border-gray-50 text-[10px] text-gray-400 font-bold tracking-wider">
                <span>COMPANY</span>
                <span>MARKET PRICE</span>
              </div>
              {[
                { name: 'CG Power & Inds', price: '₹829.45', chg: '+3.38%' },
                { name: 'Vedanta', price: '₹302.30', chg: '+2.60%' },
                { name: 'PNB', price: '₹109.25', chg: '+0.52%' }
              ].map((stock, i) => (
                <div key={i} className="grid grid-cols-2 p-4 items-center border-b border-gray-50 last:border-0">
                  <span className="font-bold text-sm">{stock.name}</span>
                  <span className="text-sm font-medium">{stock.price} <span className="text-[#00d09c] ml-1">({stock.chg})</span></span>
                </div>
              ))}
            </div>
          </section>
        </div>

        {/* Right: Sidebar Tools */}
        <div className="space-y-8">
          <section>
            <h2 className="text-lg font-bold mb-4">Your investments</h2>
            <div className="bg-white p-10 rounded-lg border border-gray-100 shadow-sm text-center">
              <img src="https://groww.in/assets/images/no_investment.svg" alt="Empty" className="w-24 mx-auto mb-4 opacity-50" />
              <p className="text-sm text-gray-400">You haven't invested yet</p>
            </div>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-4">Products & Tools</h2>
            <div className="space-y-3">
              {['IPO', 'Bonds', 'ETFs', 'Intraday Screener'].map((tool, i) => (
                <div key={i} className="bg-white p-4 rounded-lg border border-gray-100 shadow-sm flex justify-between items-center hover:border-[#00d09c] transition-colors cursor-pointer group">
                  <span className="text-sm font-medium">{tool}</span>
                  <span className="text-[#00d09c] text-[10px] font-bold opacity-0 group-hover:opacity-100 transition-opacity">EXPLORE →</span>
                </div>
              ))}
            </div>
          </section>
        </div>
      </main>

      <ChatWidget />
    </div>
  );
}
