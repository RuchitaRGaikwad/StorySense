export default function HowItWorks() {
  const steps = [
    {
      id: 1,
      title: 'Data Collection',
      subtitle: 'Gathering content metadata',
      icon: (
        <svg className="w-6 h-6 text-[#FFFDF8]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125v-3.75" />
        </svg>
      ),
      description: 'We start with datasets containing movies, TV series, and books — each with titles, descriptions, genres, ratings, and publication years.',
      detail: 'The prepare_dataset.py script normalizes all sources into a unified schema with fields: content_id, title, media_type, description, genre, year, and rating.',
    },
    {
      id: 2,
      title: 'Text Preprocessing',
      subtitle: 'Cleaning and normalizing text',
      icon: (
        <svg className="w-6 h-6 text-[#FFFDF8]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 6h9.75M10.5 6a1.5 1.5 0 11-3 0m3 0a1.5 1.5 0 10-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-9.75 0h9.75" />
        </svg>
      ),
      description: 'For each item, we combine its title, description, and genre into a single text field, then apply standard NLP preprocessing.',
      detail: 'Steps: lowercase → strip HTML tags → remove punctuation and numbers → remove English stopwords (NLTK) → lemmatize words (WordNet). This reduces noise and improves embedding quality.',
    },
    {
      id: 3,
      title: 'Sentence Embedding',
      subtitle: 'Converting text to vectors',
      icon: (
        <svg className="w-6 h-6 text-[#FFFDF8]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5m.75-9l3-1.5L12 12m0 0l3 1.5L18 12m-6 0l-3 1.5L6 12" />
        </svg>
      ),
      description: 'Each preprocessed text is encoded into a 384-dimensional dense vector using a pretrained sentence transformer model.',
      detail: 'We use all-MiniLM-L6-v2, a lightweight model (~80MB) optimized for semantic similarity tasks. It maps text to a shared embedding space where similar meanings produce vectors that are close together.',
    },
    {
      id: 4,
      title: 'Common Semantic Space',
      subtitle: 'All media in one vector space',
      icon: (
        <svg className="w-6 h-6 text-[#FFFDF8]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 017.843 4.582M12 3a8.997 8.997 0 00-7.843 4.582m15.686 0A11.953 11.953 0 0112 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0121 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0112 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 013 12c0-1.605.42-3.113 1.157-4.418" />
        </svg>
      ),
      description: 'Movies, books, and TV series all live in the same 384-dimensional vector space — enabling direct cross-media comparison.',
      detail: 'Because the model was trained on general text, it captures semantic meaning regardless of media format. A sci-fi book about space exploration maps near a sci-fi movie with similar thematic narrative.',
    },
    {
      id: 5,
      title: 'Cosine Similarity',
      subtitle: 'Measuring semantic closeness',
      icon: (
        <svg className="w-6 h-6 text-[#FFFDF8]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 14.25v2.25m3-4.5v4.5m3-6.75v6.75m3-9v9M6 20.25h12A2.25 2.25 0 0020.25 18V6A2.25 2.25 0 0018 3.75H6A2.25 2.25 0 003.75 6v12A2.25 2.25 0 006 20.25z" />
        </svg>
      ),
      description: 'For a given item, we compute the cosine similarity between its embedding and every other item in the dataset.',
      detail: 'Cosine similarity measures the angle between two vectors, ranging from -1 (opposite) to 1 (identical). It is computed as: cos(θ) = (A · B) / (||A|| × ||B||). We use scikit-learn\'s optimized implementation.',
    },
    {
      id: 6,
      title: 'Ranking & Results',
      subtitle: 'Top-N recommendations',
      icon: (
        <svg className="w-6 h-6 text-[#FFFDF8]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 18.75h-9m9 0a3 3 0 013 3h-15a3 3 0 013-3m9 0v-3.375c0-.621-.503-1.125-1.125-1.125h-.871M7.5 18.75v-3.375c0-.621.504-1.125 1.125-1.125h.872m5.007 0H9.497m5.007 0a7.454 7.454 0 01-.982-3.172M9.497 14.25a7.454 7.454 0 00.981-3.172M5.25 4.236c-.996.178-1.768.563-2.048 1.074a1.452 1.452 0 000 1.38c.28.511 1.052.896 2.048 1.074m13.5-3.528c.996.178 1.768.563 2.048 1.074a1.452 1.452 0 010 1.38c-.28.511-1.052.896-2.048 1.074M15.375 7.5a5.168 5.168 0 01-4.487 5.106m0 0a5.168 5.168 0 01-4.487-5.106M12 12.606a5.168 5.168 0 004.487-5.106M12 12.606V15m0 0h.008v.008H12V15z" />
        </svg>
      ),
      description: 'Results are ranked by similarity score and filtered by target media type. By default, we show cross-media recommendations only.',
      detail: 'Each result includes the exact similarity score, a short "why recommended" explanation (based on shared genres and theme keywords), and a description snippet.',
    },
  ]

  return (
    <div className="space-y-12 max-w-5xl mx-auto">
      {/* Page Header */}
      <div className="text-center space-y-4 py-6">
        <h1 className="text-4xl sm:text-5xl font-editorial font-bold text-[#1F3A32]">
          How <span className="italic font-normal text-[#B85C38]">StorySense</span> Works
        </h1>
        <p className="text-[#4A4A43] text-lg max-w-2xl mx-auto font-sans leading-relaxed">
          An NLP pipeline that transforms narrative descriptions into semantic vector space,
          enabling cross-media discovery between movies, books, and TV series.
        </p>
      </div>

      {/* SVG Pipeline Diagram */}
      <div className="bg-[#FFFDF8] border border-[#DDD6C8] rounded-2xl p-8 shadow-sm overflow-x-auto">
        <h2 className="text-xl font-editorial font-bold text-[#1F3A32] mb-6 text-center">Pipeline Architecture</h2>
        <svg viewBox="0 0 1100 180" className="w-full min-w-[700px]" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
              <polygon points="0 0, 10 3.5, 0 7" fill="#736E65" />
            </marker>
          </defs>

          {/* Step boxes */}
          {[
            { x: 10, label1: 'Raw Story Text', label2: 'Title + Plot + Genre' },
            { x: 230, label1: 'NLP Preprocessing', label2: 'NLTK Lemmatize' },
            { x: 450, label1: 'Vector Embedding', label2: 'MiniLM-L6-v2' },
            { x: 670, label1: 'Cosine Distance', label2: 'scikit-learn' },
            { x: 890, label1: 'Ranked Matches', label2: 'Cross-Media Top-N' },
          ].map((step, i) => (
            <g key={i}>
              <rect
                x={step.x} y="40" width="180" height="80" rx="8"
                fill="#F2F7F5" stroke="#1F3A32" strokeWidth="1.5"
              />
              <text x={step.x + 90} y="72" textAnchor="middle" fill="#1F3A32" fontSize="14" fontWeight="700" fontFamily="Newsreader, Georgia, serif">
                {step.label1}
              </text>
              <text x={step.x + 90} y="98" textAnchor="middle" fill="#736E65" fontSize="12" fontFamily="Inter, sans-serif">
                {step.label2}
              </text>

              {i < 4 && (
                <line
                  x1={step.x + 180} y1="80"
                  x2={step.x + 230} y2="80"
                  stroke="#736E65" strokeWidth="1.75" markerEnd="url(#arrowhead)"
                />
              )}
            </g>
          ))}

          <text x="540" y="155" textAnchor="middle" fill="#B85C38" fontSize="12" fontFamily="Inter, sans-serif" fontWeight="500">
            all-MiniLM-L6-v2 (384-dimensional semantic embedding matrix)
          </text>
        </svg>
      </div>

      {/* Detailed Steps */}
      <div className="space-y-6">
        {steps.map((step, index) => (
          <div key={step.id} className="relative">
            {index < steps.length - 1 && (
              <div className="absolute left-7 top-full w-0.5 h-6 bg-[#DDD6C8]" />
            )}

            <div className="bg-[#FFFDF8] border border-[#DDD6C8] rounded-xl p-6 shadow-sm">
              <div className="flex gap-5 items-start">
                <div className="shrink-0 w-14 h-14 rounded-lg bg-[#1F3A32] flex items-center justify-center text-white shadow-sm">
                  {step.icon}
                </div>

                <div className="space-y-2 flex-1">
                  <div className="flex items-baseline gap-3">
                    <span className="text-[#B85C38] text-xs font-mono font-bold uppercase tracking-wider">Step {step.id}</span>
                    <h3 className="text-xl font-editorial font-bold text-[#1F3A32]">{step.title}</h3>
                    <span className="text-[#736E65] text-sm hidden sm:inline">— {step.subtitle}</span>
                  </div>
                  <p className="text-[#4A4A43] leading-relaxed text-base">{step.description}</p>
                  <p className="text-[#736E65] text-sm leading-relaxed font-sans">{step.detail}</p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Technical Summary */}
      <div className="bg-[#FFFDF8] border border-[#DDD6C8] rounded-2xl p-8 space-y-6 shadow-sm">
        <h2 className="text-2xl font-editorial font-bold text-[#1F3A32]">Technical Specifications</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="space-y-1.5 p-4 bg-[#F2F7F5] rounded-xl border border-[#DDD6C8]">
            <h3 className="text-[#1F3A32] font-editorial font-bold text-lg">Embedding Model</h3>
            <p className="text-[#4A4A43] text-sm font-semibold">all-MiniLM-L6-v2</p>
            <p className="text-[#736E65] text-xs">Sentence Transformers · 384-dimensional dense vector space</p>
          </div>
          <div className="space-y-1.5 p-4 bg-[#F8EFEA] rounded-xl border border-[#E8D0C5]">
            <h3 className="text-[#B85C38] font-editorial font-bold text-lg">Similarity Metric</h3>
            <p className="text-[#4A4A43] text-sm font-semibold">Cosine Similarity</p>
            <p className="text-[#736E65] text-xs">scikit-learn vector dot product normalized by magnitude</p>
          </div>
          <div className="space-y-1.5 p-4 bg-[#F2F7F5] rounded-xl border border-[#DDD6C8]">
            <h3 className="text-[#1F3A32] font-editorial font-bold text-lg">Text Processing</h3>
            <p className="text-[#4A4A43] text-sm font-semibold">NLTK + WordNet</p>
            <p className="text-[#736E65] text-xs">Stopword removal · Lemmatization · HTML stripping</p>
          </div>
        </div>
      </div>
    </div>
  )
}
