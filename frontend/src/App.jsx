import { Routes, Route, Link, useLocation } from 'react-router-dom'
import Home from './pages/Home'
import ItemDetail from './pages/ItemDetail'
import HowItWorks from './pages/HowItWorks'
import Evaluation from './pages/Evaluation'
import './App.css'

const navLinks = [
  { path: '/', label: 'Search' },
  { path: '/how-it-works', label: 'How It Works' },
  { path: '/evaluation', label: 'Evaluation' },
]

function App() {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-[#F7F3EA] text-[#4A4A43] flex flex-col font-sans">
      {/* Header */}
      <header className="bg-[#1F3A32] border-b border-[#162C26] sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="flex items-center gap-3 group">
              <div className="w-9 h-9 rounded-md bg-[#294D42] border border-[#386355] flex items-center justify-center group-hover:bg-[#386355] transition-colors">
                <svg className="w-5 h-5 text-[#F7F3EA]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <span className="text-xl font-editorial font-bold text-[#F7F3EA] tracking-wide">
                Story<span className="text-[#D97745] font-serif italic">Sense</span>
              </span>
            </Link>

            <nav className="flex items-center gap-1">
              {navLinks.map((link) => {
                const isActive = location.pathname === link.path
                return (
                  <Link
                    key={link.path}
                    to={link.path}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                      isActive
                        ? 'bg-[#294D42] text-[#F7F3EA] shadow-inner'
                        : 'text-[#DDD6C8] hover:text-[#F7F3EA] hover:bg-[#294D42]/60'
                    }`}
                  >
                    {link.label}
                  </Link>
                )
              })}
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex-grow w-full">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/item/:contentId" element={<ItemDetail />} />
          <Route path="/how-it-works" element={<HowItWorks />} />
          <Route path="/evaluation" element={<Evaluation />} />
        </Routes>
      </main>

      {/* Footer */}
      <footer className="bg-[#1F3A32] border-t border-[#162C26] mt-16 text-[#DDD6C8]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <span className="font-editorial text-lg font-semibold text-[#F7F3EA]">StorySense</span>
              <span className="text-[#736E65]">•</span>
              <span className="text-xs text-[#DDD6C8]/80">NLP-Based Cross-Media Recommendation System</span>
            </div>
            <p className="text-xs text-[#DDD6C8]/70">
              Sentence Transformers (<code className="font-mono text-[#E6EEEC]">all-MiniLM-L6-v2</code>) &amp; Cosine Similarity
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
