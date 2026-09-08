import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import PosterImage from '../components/PosterImage'

const MEDIA_TYPES = [
  { value: 'all', label: 'All', icon: '+' },
  { value: 'movie', label: 'Movies', icon: '🎬' },
  { value: 'book', label: 'Books', icon: '📚' },
]

const MEDIA_BADGES = {
  movie: 'bg-[#E6EEEC] text-[#1F3A32] border-[#C5BCAB]',
  tv: 'bg-[#F2F7F5] text-[#294D42] border-[#C5BCAB]',
  book: 'bg-[#F8EFEA] text-[#B85C38] border-[#E8D0C5]',
}

// Default fallback featured items for carousel if fetch is loading
const DEFAULT_FEATURED = [
  { content_id: 'MOV010', title: 'Dune', media_type: 'movie', poster_url: 'https://image.tmdb.org/t/p/w500/v1tRXZ4JtD2Iv6fjkPvT4GiwslV.jpg' },
  { content_id: 'MOV009', title: 'Parasite', media_type: 'movie', poster_url: 'https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg' },
  { content_id: 'BK013', title: 'The Silent Patient', media_type: 'book', poster_url: 'https://covers.openlibrary.org/b/id/9407338-L.jpg' },
  { content_id: 'BK006', title: 'Sapiens', media_type: 'book', poster_url: 'https://covers.openlibrary.org/b/id/8634250-L.jpg' },
  { content_id: 'TV002', title: 'Breaking Bad', media_type: 'tv', poster_url: 'https://image.tmdb.org/t/p/w500/anFx9aTOOYqgS3v7x3R84Kz67ly.jpg' },
]

export default function Home() {
  const [query, setQuery] = useState('')
  const [mediaType, setMediaType] = useState('all')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)
  const [featuredItems, setFeaturedItems] = useState(DEFAULT_FEATURED)
  const [activeSlide, setActiveSlide] = useState(0)

  // Fetch initial featured items for carousel
  useEffect(() => {
    fetch('/api/content?query=a&limit=10')
      .then((res) => res.json())
      .then((data) => {
        if (data.results && data.results.length >= 5) {
          // Pick items with poster_url where available
          const withPosters = data.results.filter((i) => i.poster_url)
          if (withPosters.length >= 5) {
            setFeaturedItems(withPosters.slice(0, 5))
          }
        }
      })
      .catch(() => {})
  }, [])

  // Auto-slide featured carousel
  useEffect(() => {
    const timer = setInterval(() => {
      setActiveSlide((prev) => (prev + 1) % featuredItems.length)
    }, 4000)
    return () => clearInterval(timer)
  }, [featuredItems.length])

  const fetchResults = useCallback(async (q, type) => {
    if (!q.trim()) {
      setResults([])
      setHasSearched(false)
      return
    }

    setLoading(true)
    try {
      const params = new URLSearchParams({ query: q })
      if (type !== 'all') params.set('media_type', type)
      const res = await fetch(`/api/content?${params}`)
      const data = await res.json()
      setResults(data.results || [])
      setHasSearched(true)
    } catch (err) {
      console.error('Search failed:', err)
      setResults([])
    } finally {
      setLoading(false)
    }
  }, [])

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchResults(query, mediaType)
    }, 300)
    return () => clearTimeout(timer)
  }, [query, mediaType, fetchResults])

  return (
    <div className="space-y-10">
      {/* Search Section — Top of Page */}
      <div className="max-w-3xl mx-auto space-y-4">
        {/* Search Bar */}
        <div className="relative shadow-sm rounded-xl">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <svg className="w-5 h-5 text-[#736E65]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for movies, books, or TV series by title or plot..."
            className="w-full pl-12 pr-10 py-3.5 bg-[#FFFDF8] border border-[#DDD6C8] rounded-xl text-[#1F3A32] placeholder-[#736E65] focus:outline-none focus:ring-2 focus:ring-[#1F3A32]/30 focus:border-[#1F3A32] text-base transition-all shadow-sm"
          />
          {loading && (
            <div className="absolute inset-y-0 right-0 pr-4 flex items-center">
              <div className="w-5 h-5 border-2 border-[#1F3A32] border-t-transparent rounded-full animate-spin" />
            </div>
          )}
        </div>

        {/* Media Type Filter Chips */}
        <div className="flex flex-wrap gap-2 justify-center">
          {MEDIA_TYPES.map((type) => {
            const isActive = mediaType === type.value
            return (
              <button
                key={type.value}
                onClick={() => setMediaType(type.value)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-1.5 ${
                  isActive
                    ? 'bg-[#1F3A32] text-[#FFFDF8] shadow-sm hover:bg-[#162C26]'
                    : 'bg-[#FFFDF8] text-[#4A4A43] border border-[#DDD6C8] hover:bg-[#F2F7F5] hover:text-[#1F3A32]'
                }`}
              >
                <span className="text-xs font-semibold">{type.icon}</span>
                {type.label}
              </button>
            )
          })}
        </div>
      </div>

      {/* Hero Headline & Subtitle */}
      <div className="text-center space-y-3 py-2 max-w-3xl mx-auto">
        <h1 className="text-4xl sm:text-5xl font-editorial font-bold text-[#1F3A32] tracking-tight leading-tight">
          Find your next <span className="italic font-normal text-[#B85C38]">cross-media</span> story
        </h1>
        <p className="text-[#4A4A43] text-base sm:text-lg leading-relaxed font-sans max-w-2xl mx-auto">
          Discover movies, books, and web series connected by narrative themes — powered by NLP sentence embeddings and cosine similarity.
        </p>
      </div>

      {/* Featured Cover Carousel (Shows when not searching) */}
      {!hasSearched && (
        <div className="space-y-4">
          <div className="flex items-center justify-center gap-4 sm:gap-6 overflow-x-auto py-2 px-4 scrollbar-none">
            {featuredItems.map((item, idx) => (
              <Link
                key={item.content_id}
                to={`/item/${item.content_id}`}
                onClick={() => setActiveSlide(idx)}
                className={`transition-all duration-300 transform shrink-0 rounded-xl overflow-hidden shadow-md hover:shadow-xl ${
                  activeSlide === idx
                    ? 'scale-105 ring-2 ring-[#1F3A32]'
                    : 'opacity-80 hover:opacity-100 hover:scale-102'
                }`}
              >
                <PosterImage
                  src={item.poster_url}
                  alt={item.title}
                  mediaType={item.media_type}
                  size="md"
                  className="w-36 h-52 sm:w-44 sm:h-64 object-cover"
                />
              </Link>
            ))}
          </div>

          {/* Carousel Pagination Dots */}
          <div className="flex justify-center items-center gap-2">
            {featuredItems.map((_, idx) => (
              <button
                key={idx}
                onClick={() => setActiveSlide(idx)}
                className={`h-2.5 rounded-full transition-all duration-300 ${
                  activeSlide === idx ? 'w-6 bg-[#4F46E5]' : 'w-2.5 bg-[#969083]/40 hover:bg-[#969083]'
                }`}
                aria-label={`Slide ${idx + 1}`}
              />
            ))}
          </div>
        </div>
      )}

      {/* Results Section */}
      <div className="space-y-4">
        {hasSearched && (
          <div className="flex items-center justify-between text-sm text-[#736E65] border-b border-[#DDD6C8] pb-2">
            <p>
              Found <strong className="text-[#1F3A32] font-semibold">{results.length}</strong> result{results.length !== 1 ? 's' : ''} for "{query}"
            </p>
            {mediaType !== 'all' && (
              <span className="text-xs uppercase tracking-wider font-semibold text-[#B85C38]">
                Filtered by {mediaType}
              </span>
            )}
          </div>
        )}

        {hasSearched && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {results.map((item) => (
              <Link
                key={item.content_id}
                to={`/item/${item.content_id}`}
                className="group bg-[#FFFDF8] hover:bg-white border border-[#DDD6C8] hover:border-[#1F3A32]/40 rounded-xl p-4 transition-all duration-200 shadow-sm hover:shadow-md flex gap-4"
              >
                <PosterImage
                  src={item.poster_url}
                  alt={item.title}
                  mediaType={item.media_type}
                  size="sm"
                />

                <div className="flex-1 min-w-0 flex flex-col justify-between">
                  <div>
                    <div className="flex items-start justify-between gap-2 mb-1.5">
                      <h3 className="text-[#1F3A32] font-editorial font-bold text-base leading-snug group-hover:text-[#B85C38] transition-colors line-clamp-2">
                        {item.title}
                      </h3>
                      <span className={`shrink-0 px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider border ${MEDIA_BADGES[item.media_type] || 'bg-[#F2F7F5] text-[#1F3A32] border-[#DDD6C8]'}`}>
                        {item.media_type}
                      </span>
                    </div>
                    <p className="text-[#4A4A43] text-xs line-clamp-2 leading-relaxed">
                      {item.description}
                    </p>
                  </div>

                  <div className="flex items-center justify-between pt-2 mt-2 border-t border-[#DDD6C8]/60 text-[10px] text-[#736E65]">
                    <span className="truncate font-medium max-w-[140px]">
                      {item.genre ? item.genre.split(',').slice(0, 2).join(', ') : 'Story'}
                    </span>
                    <div className="flex items-center gap-2 shrink-0 font-medium">
                      {item.year > 0 && <span>{item.year}</span>}
                      {item.avg_rating && <span className="text-[#B85C38]">★ {item.avg_rating}</span>}
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}

        {hasSearched && results.length === 0 && !loading && (
          <div className="text-center py-12 bg-[#FFFDF8] border border-[#DDD6C8] rounded-xl p-8 max-w-xl mx-auto">
            <p className="text-[#1F3A32] font-editorial text-xl font-semibold mb-1">No matching stories found</p>
            <p className="text-[#736E65] text-sm">Try broadening your search term or selecting 'All' media types.</p>
          </div>
        )}

        {!hasSearched && (
          <div className="text-center py-10 space-y-4 max-w-md mx-auto">
            {/* Story Discovery Icon */}
            <div className="w-14 h-14 mx-auto rounded-full bg-[#E6EEEC] border border-[#DDD6C8] flex items-center justify-center text-[#1F3A32] shadow-sm">
              <svg className="w-7 h-7 text-[#1F3A32]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <h2 className="text-[#1F3A32] font-editorial text-2xl font-bold">
              Explore cross-media narratives
            </h2>
            <p className="text-[#4A4A43] text-sm leading-relaxed">
              Search by title or theme to discover how stories move across literature, film, and television.
            </p>
            <div className="pt-2 flex flex-wrap justify-center gap-2 text-xs">
              <span className="text-[#736E65]">Try searching:</span>
              <button onClick={() => setQuery("space adventure")} className="text-[#B85C38] hover:underline font-medium">"space adventure"</button>
              <span className="text-[#736E65]">•</span>
              <button onClick={() => setQuery("dystopian future")} className="text-[#B85C38] hover:underline font-medium">"dystopian future"</button>
              <span className="text-[#736E65]">•</span>
              <button onClick={() => setQuery("detective mystery")} className="text-[#B85C38] hover:underline font-medium">"detective mystery"</button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
