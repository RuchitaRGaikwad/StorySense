import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'

const MEDIA_COLORS = {
  movie: { bg: 'bg-[#E6EEEC]', text: 'text-[#1F3A32]', border: 'border-[#C5BCAB]', leftBorder: 'border-l-[#1F3A32]', topBg: 'bg-[#E6EEEC]' },
  tv: { bg: 'bg-[#F2F7F5]', text: 'text-[#294D42]', border: 'border-[#C5BCAB]', leftBorder: 'border-l-[#294D42]', topBg: 'bg-[#F2F7F5]' },
  book: { bg: 'bg-[#F8EFEA]', text: 'text-[#B85C38]', border: 'border-[#E8D0C5]', leftBorder: 'border-l-[#B85C38]', topBg: 'bg-[#F8EFEA]' },
}

const MEDIA_ICONS = {
  movie: '🎬',
  tv: '📺',
  book: '📚',
}

function SimilarityBar({ score }) {
  const pct = Math.round(score * 100)
  let barBg = 'bg-[#B85C38]' // terracotta
  if (pct >= 70) barBg = 'bg-[#1F3A32]' // forest green
  else if (pct >= 50) barBg = 'bg-[#386355]'
  else if (pct >= 30) barBg = 'bg-[#C46743]'

  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 h-2 bg-[#E6EEEC] rounded-full overflow-hidden">
        <div
          className={`h-full ${barBg} rounded-full transition-all duration-500 ease-out`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-sm font-semibold text-[#1F3A32] tabular-nums w-12 text-right">
        {pct}%
      </span>
    </div>
  )
}

export default function ItemDetail() {
  const { contentId } = useParams()
  const [item, setItem] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const [metadata, setMetadata] = useState(null)
  const [loading, setLoading] = useState(true)
  const [recLoading, setRecLoading] = useState(true)
  const [error, setError] = useState(null)
  const [includeSameMedia, setIncludeSameMedia] = useState(false)
  const [topN, setTopN] = useState(8)

  // Fetch item detail
  useEffect(() => {
    setLoading(true)
    setError(null)
    fetch(`/api/content/${contentId}`)
      .then((res) => {
        if (!res.ok) throw new Error(`Item not found (${res.status})`)
        return res.json()
      })
      .then((data) => {
        setItem(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [contentId])

  // Fetch recommendations
  useEffect(() => {
    setRecLoading(true)
    const params = new URLSearchParams({
      top_n: topN.toString(),
      include_same_media: includeSameMedia.toString(),
    })
    fetch(`/api/recommend/${contentId}?${params}`)
      .then((res) => res.json())
      .then((data) => {
        setRecommendations(data.recommendations || [])
        setMetadata(data.metadata || null)
        setRecLoading(false)
      })
      .catch(() => setRecLoading(false))
  }, [contentId, includeSameMedia, topN])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="w-8 h-8 border-2 border-[#1F3A32] border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-20 space-y-4 bg-[#FFFDF8] border border-[#DDD6C8] rounded-xl p-8 max-w-lg mx-auto">
        <p className="text-[#B85C38] font-editorial text-2xl font-bold">{error}</p>
        <Link to="/" className="inline-block px-5 py-2.5 bg-[#1F3A32] text-[#FFFDF8] rounded-lg hover:bg-[#162C26] transition-colors text-sm font-medium">
          ← Back to Search
        </Link>
      </div>
    )
  }

  const mc = MEDIA_COLORS[item?.media_type?.toLowerCase()] || MEDIA_COLORS.movie

  return (
    <div className="space-y-10">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-sm text-[#736E65]">
        <Link to="/" className="hover:text-[#1F3A32] transition-colors font-medium">Search</Link>
        <span>/</span>
        <span className="text-[#1F3A32] font-semibold truncate max-w-xs">{item?.title}</span>
      </nav>

      {/* Source Item Card */}
      <div className="bg-[#FFFDF8] border border-[#DDD6C8] rounded-2xl p-8 shadow-sm space-y-5 relative overflow-hidden">
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <span className="text-3xl">{MEDIA_ICONS[item?.media_type?.toLowerCase()] || '📄'}</span>
              <h1 className="text-3xl sm:text-4xl font-editorial font-bold text-[#1F3A32] leading-tight">{item?.title}</h1>
            </div>
            <div className="flex items-center gap-3 flex-wrap">
              <span className={`px-3 py-1 rounded text-xs font-bold uppercase tracking-wider ${mc.bg} ${mc.text} border ${mc.border}`}>
                {item?.media_type}
              </span>
              {item?.year > 0 && (
                <span className="text-[#736E65] text-sm font-medium">📅 {item.year}</span>
              )}
              {item?.avg_rating && (
                <span className="text-[#B85C38] text-sm font-semibold">★ {item.avg_rating}</span>
              )}
            </div>
          </div>
        </div>

        {item?.genre && (
          <div className="flex flex-wrap gap-2">
            {item.genre.split(',').map((g, i) => (
              <span key={i} className="px-3 py-1 bg-[#F2F7F5] text-[#1F3A32] border border-[#DDD6C8] rounded-md text-xs font-medium">
                {g.trim()}
              </span>
            ))}
          </div>
        )}

        <p className="text-[#4A4A43] leading-relaxed text-base max-w-4xl font-sans">
          {item?.description}
        </p>
      </div>

      {/* Recommendations Section */}
      <section className="space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-2 border-b border-[#DDD6C8]">
          <div>
            <h2 className="text-2xl font-editorial font-bold text-[#1F3A32]">
              Recommended Across Media
            </h2>
            <p className="text-[#736E65] text-sm mt-0.5">
              Powered by real cosine similarity on sentence-transformer embeddings
            </p>
          </div>

          <div className="flex items-center gap-3 flex-wrap">
            {/* Top-N selector */}
            <div className="flex items-center gap-2">
              <label className="text-[#736E65] text-xs font-medium uppercase tracking-wider">Show</label>
              <select
                value={topN}
                onChange={(e) => setTopN(Number(e.target.value))}
                className="bg-[#FFFDF8] border border-[#DDD6C8] text-[#1F3A32] rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#1F3A32]/30 font-medium"
              >
                {[5, 8, 10, 15, 20].map((n) => (
                  <option key={n} value={n}>{n}</option>
                ))}
              </select>
            </div>

            {/* Cross-media toggle */}
            <button
              onClick={() => setIncludeSameMedia(!includeSameMedia)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                includeSameMedia
                  ? 'bg-[#1F3A32] text-[#FFFDF8] shadow-sm hover:bg-[#162C26]'
                  : 'bg-[#FFFDF8] text-[#4A4A43] border border-[#DDD6C8] hover:bg-[#F2F7F5]'
              }`}
            >
              <span className={`w-2.5 h-2.5 rounded-full ${includeSameMedia ? 'bg-[#D97745]' : 'bg-[#C5BCAB]'}`} />
              {includeSameMedia ? 'All Media Types' : 'Cross-Media Only'}
            </button>
          </div>
        </div>

        {/* Computation metadata */}
        {metadata && (
          <div className="flex flex-wrap gap-4 text-xs text-[#736E65] bg-[#FFFDF8] border border-[#DDD6C8] rounded-lg px-4 py-2.5 font-mono">
            <span>⚡ {metadata.computation_time_ms}ms query time</span>
            <span>📊 {metadata.total_items_compared} items compared</span>
            <span>🔍 {includeSameMedia ? 'Including' : 'Excluding'} same media type</span>
          </div>
        )}

        {/* Recommendations Grid */}
        {recLoading ? (
          <div className="flex items-center justify-center py-16">
            <div className="w-8 h-8 border-2 border-[#1F3A32] border-t-transparent rounded-full animate-spin" />
          </div>
        ) : recommendations.length === 0 ? (
          <div className="text-center py-16 text-[#736E65] bg-[#FFFDF8] border border-[#DDD6C8] rounded-xl">
            No recommendations found. Try enabling "All Media Types" mode.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
            {recommendations.map((rec, index) => {
              const rc = MEDIA_COLORS[rec.media_type?.toLowerCase()] || MEDIA_COLORS.movie
              return (
                <Link
                  key={rec.content_id}
                  to={`/item/${rec.content_id}`}
                  className={`group bg-[#FFFDF8] hover:bg-white border border-[#DDD6C8] hover:border-[#1F3A32]/40 rounded-xl overflow-hidden transition-all duration-200 shadow-sm hover:shadow-md border-l-4 ${rc.leftBorder} flex flex-col justify-between`}
                  style={{ animationDelay: `${index * 40}ms` }}
                >
                  {/* Media type header bar */}
                  <div>
                    <div className={`${rc.topBg} px-5 py-2.5 flex items-center justify-between border-b border-[#DDD6C8]/60`}>
                      <div className="flex items-center gap-2">
                        <span className="text-lg">{MEDIA_ICONS[rec.media_type?.toLowerCase()]}</span>
                        <span className={`text-xs font-bold uppercase tracking-wider ${rc.text}`}>
                          {rec.media_type}
                        </span>
                      </div>
                      <span className={`px-2 py-0.5 rounded text-xs font-semibold ${rc.bg} ${rc.text} border ${rc.border}`}>
                        {rec.similarity_pct}% match
                      </span>
                    </div>

                    <div className="p-5 space-y-3">
                      {/* Title */}
                      <h3 className="text-[#1F3A32] font-editorial font-bold text-lg leading-snug group-hover:text-[#B85C38] transition-colors line-clamp-2">
                        {rec.title}
                      </h3>

                      {/* Similarity bar */}
                      <SimilarityBar score={rec.similarity_score} />

                      {/* Why */}
                      <p className="text-[#B85C38] text-xs font-medium line-clamp-2 leading-relaxed">
                        💡 {rec.why}
                      </p>

                      {/* Description */}
                      <p className="text-[#4A4A43] text-sm line-clamp-3 leading-relaxed">
                        {rec.description}
                      </p>
                    </div>
                  </div>

                  {/* Genre tags */}
                  {rec.genre && (
                    <div className="px-5 pb-4 pt-1 flex flex-wrap gap-1.5">
                      {rec.genre.split(',').slice(0, 3).map((g, i) => (
                        <span key={i} className="px-2 py-0.5 bg-[#F2F7F5] text-[#1F3A32] border border-[#DDD6C8] rounded text-xs">
                          {g.trim()}
                        </span>
                      ))}
                    </div>
                  )}
                </Link>
              )
            })}
          </div>
        )}
      </section>

      {/* Disclaimer */}
      <div className="bg-[#FFFDF8] border border-[#DDD6C8] rounded-lg p-4 text-center">
        <p className="text-[#736E65] text-xs">
          ⚠️ Prototype-scale results on sample dataset. Similarity scores computed live
          using <code className="font-mono text-[#1F3A32]">all-MiniLM-L6-v2</code> embeddings and cosine similarity — not hardcoded or mocked.
        </p>
      </div>
    </div>
  )
}
