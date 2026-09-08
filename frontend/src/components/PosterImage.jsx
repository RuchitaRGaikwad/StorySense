import { useState } from 'react'

const MEDIA_ICONS = {
  movie: '🎬',
  tv: '📺',
  book: '📚',
}

const PLACEHOLDER_BG = {
  movie: 'bg-[#E6EEEC]',
  tv: 'bg-[#F2F7F5]',
  book: 'bg-[#F8EFEA]',
}

/**
 * Renders a poster/cover image with a graceful fallback placeholder.
 * @param {string} src - poster_url from API
 * @param {string} alt - alt text (usually the title)
 * @param {string} mediaType - 'movie' | 'tv' | 'book'
 * @param {string} className - wrapper className override
 * @param {string} size - 'sm' | 'md' | 'lg' for preset dimensions
 */
export default function PosterImage({ src, alt, mediaType = 'movie', className = '', size = 'md' }) {
  const [failed, setFailed] = useState(false)
  const showPlaceholder = !src || failed

  const sizeClasses = {
    sm: 'w-14 h-20',
    md: 'w-24 h-36',
    lg: 'w-40 h-60',
  }

  const iconSize = {
    sm: 'text-xl',
    md: 'text-3xl',
    lg: 'text-5xl',
  }

  const dimensions = sizeClasses[size] || sizeClasses.md

  if (showPlaceholder) {
    return (
      <div className={`${dimensions} rounded-lg ${PLACEHOLDER_BG[mediaType] || 'bg-[#E6EEEC]'} border border-[#DDD6C8] flex items-center justify-center shrink-0 ${className}`}>
        <span className={`${iconSize[size]} opacity-60`}>
          {MEDIA_ICONS[mediaType] || '📄'}
        </span>
      </div>
    )
  }

  return (
    <img
      src={src}
      alt={alt}
      loading="lazy"
      onError={() => setFailed(true)}
      className={`${dimensions} rounded-lg object-cover shrink-0 border border-[#DDD6C8] shadow-sm ${className}`}
    />
  )
}
