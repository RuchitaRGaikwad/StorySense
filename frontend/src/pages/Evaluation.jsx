import { useState, useEffect } from 'react'

function MetricCard({ label, value, unit, description, highlight = false }) {
  return (
    <div className={`bg-[#FFFDF8] border ${highlight ? 'border-[#B85C38]' : 'border-[#DDD6C8]'} rounded-xl p-5 space-y-1.5 shadow-sm`}>
      <p className="text-[#736E65] text-xs uppercase tracking-wider font-semibold">{label}</p>
      <div className="flex items-baseline gap-1">
        <span className={`text-3xl font-editorial font-bold ${highlight ? 'text-[#B85C38]' : 'text-[#1F3A32]'} tabular-nums`}>{value}</span>
        {unit && <span className="text-[#736E65] text-sm">{unit}</span>}
      </div>
      {description && <p className="text-[#736E65] text-xs">{description}</p>}
    </div>
  )
}

function StatBar({ label, value, max = 1, barColor = 'bg-[#1F3A32]' }) {
  const pct = Math.min((value / max) * 100, 100)
  return (
    <div className="space-y-1.5">
      <div className="flex justify-between items-baseline">
        <span className="text-[#4A4A43] text-sm font-medium">{label}</span>
        <span className="text-[#1F3A32] text-sm font-bold tabular-nums">{(value * 100).toFixed(1)}%</span>
      </div>
      <div className="h-2.5 bg-[#E6EEEC] rounded-full overflow-hidden">
        <div
          className={`h-full ${barColor} rounded-full transition-all duration-700`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}

export default function Evaluation() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    fetch('/api/evaluate')
      .then((res) => {
        if (!res.ok) throw new Error(`Server error (${res.status})`)
        return res.json()
      })
      .then((d) => {
        setData(d)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 space-y-4">
        <div className="w-10 h-10 border-2 border-[#1F3A32] border-t-transparent rounded-full animate-spin" />
        <p className="text-[#4A4A43] text-sm font-medium">Computing live evaluation metrics on the dataset…</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-20 bg-[#FFFDF8] border border-[#DDD6C8] rounded-xl p-8 max-w-lg mx-auto space-y-3">
        <p className="text-[#B85C38] font-editorial text-2xl font-bold">Failed to load evaluation: {error}</p>
        <p className="text-[#736E65] text-sm">Please ensure the backend API server is running on port 8000.</p>
      </div>
    )
  }

  const ds = data?.dataset_stats || {}
  const sim = data?.similarity_metrics || {}
  const perf = data?.performance_metrics || {}

  return (
    <div className="space-y-10 max-w-5xl mx-auto">
      {/* Header */}
      <div className="text-center space-y-3 py-6">
        <h1 className="text-4xl sm:text-5xl font-editorial font-bold text-[#1F3A32]">
          Evaluation <span className="italic font-normal text-[#B85C38]">Metrics</span>
        </h1>
        <p className="text-[#4A4A43] text-lg max-w-2xl mx-auto leading-relaxed">
          Real evaluation statistics computed live on the loaded dataset.
          All metrics originate from actual vector cosine similarity calculations.
        </p>
      </div>

      {/* Disclaimer Banner */}
      <div className="bg-[#F8EFEA] border border-[#E8D0C5] rounded-xl p-5 flex items-start gap-4 shadow-sm">
        <span className="text-2xl shrink-0">📊</span>
        <div>
          <p className="text-[#B85C38] font-bold text-sm">Prototype-Scale Results on Sample Dataset</p>
          <p className="text-[#4A4A43] text-xs mt-1 leading-relaxed">
            {data?.disclaimer || 'These metrics are computed on a sample dataset to demonstrate the functioning NLP pipeline. They represent prototype metrics rather than final paper benchmarks.'}
          </p>
        </div>
      </div>

      {/* Dataset Stats */}
      <section className="space-y-4">
        <h2 className="text-2xl font-editorial font-bold text-[#1F3A32]">
          Dataset Overview
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <MetricCard
            label="Total Items"
            value={ds.total_items?.toLocaleString() || '—'}
            description="Unified cross-media dataset"
          />
          <MetricCard
            label="Movies & TV"
            value={ds.movies_tv?.toLocaleString() || '—'}
            description="Film and series entries"
          />
          <MetricCard
            label="Books"
            value={ds.books?.toLocaleString() || '—'}
            description="Book entries"
          />
          <MetricCard
            label="Vector Dim"
            value={ds.embedding_dimension || '—'}
            description={ds.model || 'Sentence Transformer'}
            highlight
          />
        </div>
      </section>

      {/* Similarity Metrics */}
      <section className="space-y-4">
        <h2 className="text-2xl font-editorial font-bold text-[#1F3A32]">
          Cross-Media Similarity Distribution
        </h2>
        <p className="text-[#736E65] text-sm">
          Evaluated across a random sample of {sim.sample_size || '—'} items · Cross-media matches only (excluding same media type)
        </p>

        <div className="bg-[#FFFDF8] border border-[#DDD6C8] rounded-xl p-6 space-y-5 shadow-sm">
          <StatBar
            label="Average Top-1 Similarity"
            value={sim.avg_top1_similarity || 0}
            barColor="bg-[#1F3A32]"
          />
          <StatBar
            label="Average Top-5 Similarity"
            value={sim.avg_top5_similarity || 0}
            barColor="bg-[#386355]"
          />
          <StatBar
            label="Maximum Top-1 Similarity"
            value={sim.max_top1_similarity || 0}
            barColor="bg-[#B85C38]"
          />
          <StatBar
            label="Minimum Top-1 Similarity"
            value={sim.min_top1_similarity || 0}
            barColor="bg-[#C46743]"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard
            label="Std Dev (Top-1)"
            value={sim.std_top1_similarity?.toFixed(4) || '—'}
            description="Standard deviation of top matches"
          />
          <MetricCard
            label="Sample Evaluated"
            value={sim.sample_size || '—'}
            unit="items"
            description="Subsample size for evaluation"
          />
          <MetricCard
            label="Model Name"
            value={ds.model?.replace('all-', '') || '—'}
            description="Sentence Transformer model"
            highlight
          />
        </div>
      </section>

      {/* Performance Metrics */}
      <section className="space-y-4">
        <h2 className="text-2xl font-editorial font-bold text-[#1F3A32]">
          Response Latency
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard
            label="Avg Query Latency"
            value={perf.avg_query_time_ms || '—'}
            unit="ms"
            description="Average recommendation time"
          />
          <MetricCard
            label="Max Query Latency"
            value={perf.max_query_time_ms || '—'}
            unit="ms"
            description="Slowest individual query"
          />
          <MetricCard
            label="Total Eval Runtime"
            value={perf.total_eval_time_s || '—'}
            unit="sec"
            description="Overall metric computation time"
          />
        </div>
      </section>

      {/* Methodology Note */}
      <div className="bg-[#FFFDF8] border border-[#DDD6C8] rounded-xl p-6 space-y-3 shadow-sm">
        <h3 className="text-xl font-editorial font-bold text-[#1F3A32]">Evaluation Methodology</h3>
        <ul className="text-[#4A4A43] text-sm space-y-2 list-disc list-inside leading-relaxed font-sans">
          <li>A random subset of dataset items is sampled using a fixed random seed for consistency.</li>
          <li>For each item, exact cosine similarity is computed against all items of alternative media types.</li>
          <li>Top-1 and Top-5 similarity scores are tracked along with per-query response latency.</li>
          <li>Metrics are aggregated to produce mean, range, and standard deviation stats.</li>
        </ul>
      </div>
    </div>
  )
}
