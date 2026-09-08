import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import PosterImage from '../components/PosterImage'

const MEDIA_COLORS = {
  movie: { bg: 'bg-[#1F3A32] text-white', text: 'text-[#1F3A32]', border: 'border-[#C5BCAB]', leftBorder: 'border-l-[#1F3A32]', topBg: 'bg-[#E6EEEC]' },
  tv: { bg: 'bg-[#1F3A32] text-white', text: 'text-[#294D42]', border: 'border-[#C5BCAB]', leftBorder: 'border-l-[#294D42]', topBg: 'bg-[#F2F7F5]' },
  book: { bg: 'bg-[#B85C38] text-white', text: 'text-[#B85C38]', border: 'border-[#E8D0C5]', leftBorder: 'border-l-[#B85C38]', topBg: 'bg-[#F8EFEA]' },
}

const MEDIA_ICONS = {
  movie: '🎬',
  tv: '📺',
  book: '📚',
}

export default function ItemDetail() {
  const { contentId } = useParams()
  const navigate = useNavigate()
  const [item, setItem] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const [metadata, setMetadata] = useState(null)
  const [loading, setLoading] = useState(true)
  const [recLoading, setRecLoading] = useState(true)
  const [error, setError] = useState(null)
  const [includeSameMedia, setIncludeSameMedia] = useState(false)
  const [topN, setTopN] = useState(8)
  const [searchQuery, setSearchQuery] = useState('')
  const [discoveryChain, setDiscoveryChain] = useState([])

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
        const recs = data.recommendations || []
        setRecommendations(recs)
        setMetadata(data.metadata || null)
        setRecLoading(false)

        // Build Discovery of the Week chain if recommendations exist
        if (recs.length >= 3 && item) {
          setDiscoveryChain([
            { content_id: item.content_id, title: item.title, media_type: item.media_type, poster_url: item.poster_url },
            ...recs.slice(0, 3).map((r) => ({ content_id: r.content_id, title: r.title, media_type: r.media_type, poster_url: r.poster_url }))
          ])
        }
      })
      .catch(() => setRecLoading(false))
  }, [contentId, includeSameMedia, topN, item])

  const handleMiniSearch = (e) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      navigate(`/?query=${encodeURIComponent(searchQuery)}`)
    }
  }

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
    <div className="space-y-12">
      {/* Top Controls Bar: Breadcrumb + Mini Search Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-sm text-[#736E65]">
          <Link to="/" className="hover:text-[#1F3A32] transition-colors font-medium">Search</Link>
          <span>/</span>
          <span className="text-[#1F3A32] font-semibold truncate max-w-xs">{item?.title}</span>
        </nav>

        {/* Mini Search & Category Controls */}
        <form onSubmit={handleMiniSearch} className="flex items-center gap-2">
          <div className="relative shadow-sm rounded-lg flex-1 md:w-64">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search for movies, by title or plot..."
              className="w-full pl-3 pr-8 py-1.5 bg-[#FFFDF8] border border-[#DDD6C8] rounded-lg text-xs text-[#1F3A32] placeholder-[#736E65] focus:outline-none focus:ring-1 focus:ring-[#1F3A32]"
            />
            <button type="submit" className="absolute right-2 top-2 text-[#736E65]">
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </button>
          </div>

          <div className="flex gap-1">
            <button type="button" onClick={() => navigate('/')} className="px-2.5 py-1 bg-[#1F3A32] text-white rounded text-xs font-semibold">+ All</button>
            <button type="button" onClick={() => navigate('/')} className="px-2.5 py-1 bg-[#FFFDF8] border border-[#DDD6C8] text-[#4A4A43] rounded text-xs font-medium">🎬 Movies</button>
            <button type="button" onClick={() => navigate('/')} className="px-2.5 py-1 bg-[#FFFDF8] border border-[#DDD6C8] text-[#4A4A43] rounded text-xs font-medium">📚 Books</button>
          </div>
        </form>
      </div>

      {/* Item Focus Section */}
      <div className="space-y-3">
        <h2 className="text-xl font-editorial font-bold text-[#1F3A32]">Item Focus</h2>

        {/* Source Item Card */}
        <div className="bg-[#FFFDF8] border border-[#DDD6C8] rounded-2xl p-6 shadow-sm relative overflow-hidden">
          <div className="flex flex-col sm:flex-row gap-6 items-start">
            {/* Poster */}
            <PosterImage
              src={item?.poster_url}
              alt={item?.title}
              mediaType={item?.media_type?.toLowerCase()}
              size="lg"
              className="w-36 h-52 sm:w-44 sm:h-64 object-cover shadow-md rounded-xl"
            />

            {/* Content Details */}
            <div className="flex-1 space-y-3">
              <div className="flex items-center gap-3 flex-wrap">
                <h1 className="text-3xl sm:text-4xl font-editorial font-bold text-[#1F3A32] leading-tight">{item?.title}</h1>
              </div>

              <div className="flex items-center gap-3 flex-wrap">
                <span className={`px-2.5 py-0.5 rounded text-xs font-bold uppercase tracking-wider ${mc.bg}`}>
                  {item?.media_type}
                </span>
                {item?.year > 0 && (
                  <span className="text-[#736E65] text-xs font-medium flex items-center gap-1">
                    📅 {item.year}
                  </span>
                )}
                {item?.avg_rating && (
                  <span className="text-[#B85C38] text-xs font-bold flex items-center gap-1">
                    ★ {item.avg_rating}/10
                  </span>
                )}
              </div>

              <p className="text-[#4A4A43] leading-relaxed text-sm max-w-3xl font-sans">
                {item?.description}
              </p>

              {item?.genre && (
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {item.genre.split(',').map((g, i) => (
                    <span key={i} className="px-2.5 py-1 bg-[#FFFDF8] text-[#4A4A43] border border-[#DDD6C8] rounded-md text-xs font-medium">
                      {g.trim()}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Explore Similar Narratives - Multi-Media Connections */}
      <section className="space-y-6 relative">
        {/* Branching Connection Lines Visualization */}
        <div className="hidden lg:block absolute -top-6 left-1/2 -translate-x-1/2 w-3/4 h-8 pointer-events-none opacity-30">
          <svg className="w-full h-full" viewBox="0 0 800 30" fill="none">
            <path d="M400 0 C 400 20, 150 10, 150 30 M400 0 C 400 20, 400 10, 400 30 M400 0 C 400 20, 650 10, 650 30" stroke="#1F3A32" strokeWidth="1.5" strokeDasharray="4 4" />
          </svg>
        </div>

        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-2 border-b border-[#DDD6C8]">
          <div>
            <h2 className="text-2xl font-editorial font-bold text-[#1F3A32]">
              Explore Similar Narratives - Multi-Media Connections
            </h2>
            <p className="text-[#736E65] text-xs mt-0.5">
              Powered by real cosine similarity on sentence-transformer embeddings
            </p>
          </div>

          <div className="flex items-center gap-3 flex-wrap">
            <div className="flex items-center gap-2">
              <label className="text-[#736E65] text-xs font-medium uppercase tracking-wider">Show</label>
              <select
                value={topN}
                onChange={(e) => setTopN(Number(e.target.value))}
                className="bg-[#FFFDF8] border border-[#DDD6C8] text-[#1F3A32] rounded-lg px-3 py-1.5 text-xs focus:outline-none font-medium"
              >
                {[5, 8, 10, 15, 20].map((n) => (
                  <option key={n} value={n}>{n}</option>
                ))}
              </select>
            </div>

            <button
              onClick={() => setIncludeSameMedia(!includeSameMedia)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                includeSameMedia
                  ? 'bg-[#1F3A32] text-[#FFFDF8] shadow-sm'
                  : 'bg-[#FFFDF8] text-[#4A4A43] border border-[#DDD6C8] hover:bg-[#F2F7F5]'
              }`}
            >
              <span className={`w-2 h-2 rounded-full ${includeSameMedia ? 'bg-[#D97745]' : 'bg-[#C5BCAB]'}`} />
              {includeSameMedia ? 'All Media Types' : 'Cross-Media Only'}
            </button>
          </div>
        </div>

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
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            {recommendations.map((rec) => {
              const rtype = rec.media_type?.toLowerCase() || 'movie'
              const badgeStyle = rtype === 'book' ? 'bg-[#B85C38] text-white' : 'bg-[#1F3A32] text-white'

              return (
                <Link
                  key={rec.content_id}
                  to={`/item/${rec.content_id}`}
                  className="group bg-[#FFFDF8] hover:bg-white border border-[#DDD6C8] hover:border-[#1F3A32]/40 rounded-2xl overflow-hidden transition-all duration-300 shadow-sm hover:shadow-lg flex flex-col justify-between"
                >
                  <div>
                    {/* Top Poster Image Banner */}
                    <div className="relative h-44 w-full bg-[#E6EEEC] overflow-hidden">
                      {rec.poster_url ? (
                        <img
                          src={rec.poster_url}
                          alt={rec.title}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-4xl opacity-40">
                          {MEDIA_ICONS[rtype]}
                        </div>
                      )}

                      {/* Overlaid Badges */}
                      <div className="absolute top-3 left-3">
                        <span className={`px-2.5 py-1 rounded text-[11px] font-bold uppercase tracking-wider ${badgeStyle} shadow-sm`}>
                          {rec.media_type}
                        </span>
                      </div>

                      <div className="absolute top-3 right-3 bg-[#FFFDF8]/95 border border-[#DDD6C8] px-2.5 py-1 rounded text-xs font-bold text-[#1F3A32] shadow-sm">
                        {rec.similarity_pct}%
                      </div>
                    </div>

                    {/* Content Section */}
                    <div className="p-5 space-y-3">
                      <h3 className="text-[#1F3A32] font-editorial font-bold text-lg leading-snug group-hover:text-[#B85C38] transition-colors line-clamp-1">
                        {rec.title}
                      </h3>

                      <p className="text-[#4A4A43] text-xs font-medium line-clamp-2 leading-relaxed">
                        High narrative theme match ({rec.similarity_pct}%): {rec.why}
                      </p>

                      {rec.genre && (
                        <div className="flex flex-wrap gap-1.5 pt-1">
                          {rec.genre.split(',').slice(0, 3).map((g, i) => (
                            <span key={i} className="px-2 py-0.5 bg-[#FFFDF8] text-[#4A4A43] border border-[#DDD6C8] rounded text-[11px]">
                              {g.trim()}
                            </span>
                          ))}
                        </div>
                      )}

                      <p className="text-[#736E65] text-xs line-clamp-2 leading-relaxed pt-1">
                        {rec.description}
                      </p>
                    </div>
                  </div>
                </Link>
              )
            })}
          </div>
        )}
      </section>

      {/* Discovery of the Week (Narrative Flow Chain) */}
      {discoveryChain.length > 0 && (
        <section className="bg-[#FFFDF8] border border-[#DDD6C8] rounded-2xl p-6 space-y-4 shadow-sm">
          <div>
            <h2 className="text-xl font-editorial font-bold text-[#1F3A32]">
              Discovery of the Week
            </h2>
            <p className="text-[#736E65] text-xs">
              From est:liver: unintended consequences.
            </p>
          </div>

          <div className="flex items-center gap-3 overflow-x-auto py-2">
            {discoveryChain.map((chainItem, idx) => (
              <div key={chainItem.content_id} className="flex items-center gap-3 shrink-0">
                <Link
                  to={`/item/${chainItem.content_id}`}
                  className="group relative w-28 h-36 rounded-xl overflow-hidden border border-[#DDD6C8] shadow-sm hover:shadow-md hover:scale-105 transition-all"
                >
                  <PosterImage
                    src={chainItem.poster_url}
                    alt={chainItem.title}
                    mediaType={chainItem.media_type}
                    size="sm"
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent flex items-end p-2">
                    <span className="text-white text-[11px] font-bold truncate leading-tight">
                      {chainItem.title}
                    </span>
                  </div>
                </Link>

                {idx < discoveryChain.length - 1 && (
                  <span className="text-[#736E65] text-lg font-bold">→</span>
                )}
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
