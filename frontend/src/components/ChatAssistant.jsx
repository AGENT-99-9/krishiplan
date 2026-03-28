import { useMemo, useState } from 'react';

/**
 * Enhanced RAG-aware message renderer.
 * Supports bold, bullet points, numbered lists, and sections.
 */
function FormattedMessage({ text }) {
    const rendered = useMemo(() => {
        if (!text) return null;

        const lines = text.split('\n');
        return lines.map((line, i) => {
            const trimmed = line.trim();

            // Sections / H3 (### Section)
            if (trimmed.startsWith('###')) {
                const content = trimmed.replace(/^###\s*/, '');
                return (
                    <h3 key={i} className="text-lg font-extrabold text-gray-900 mt-6 mb-3 flex items-center gap-2 border-l-4 border-green-500 pl-3">
                        {content}
                    </h3>
                );
            }

            // Sub-sections / Bold headers (**Header**)
            if (trimmed.startsWith('**') && trimmed.endsWith('**')) {
                const content = trimmed.replace(/^\*\*/, '').replace(/\*\*$/, '');
                return <h4 key={i} className="font-bold text-[15px] mt-4 mb-2 text-green-800">{content}</h4>;
            }

            // Bold conversion within lines
            let formatted = line;
            const parts = [];
            const regex = /\*\*(.*?)\*\*/g;
            let lastIndex = 0;
            let match;

            while ((match = regex.exec(formatted)) !== null) {
                if (match.index > lastIndex) {
                    parts.push(<span key={`${i}-${lastIndex}`}>{formatted.slice(lastIndex, match.index)}</span>);
                }
                parts.push(<strong key={`${i}-b-${match.index}`} className="font-bold text-gray-900 underline decoration-green-300 underline-offset-2 decoration-2">{match[1]}</strong>);
                lastIndex = regex.lastIndex;
            }
            if (lastIndex < formatted.length) {
                parts.push(<span key={`${i}-end`}>{formatted.slice(lastIndex)}</span>);
            }

            // Bullet points
            if (trimmed.startsWith('•') || trimmed.startsWith('-') || (trimmed.startsWith('*') && !trimmed.startsWith('**'))) {
                const bulletContent = trimmed.replace(/^[•\-\*]\s*/, '');
                return (
                    <div key={i} className="group flex items-start gap-3 ml-1 my-2 hover:translate-x-1 transition-transform">
                        <div className="mt-1.5 w-1.5 h-1.5 rounded-full bg-green-500 shadow-sm shrink-0" />
                        <span className="text-gray-700 leading-relaxed font-medium">{parts.length > 1 ? parts : bulletContent}</span>
                    </div>
                );
            }

            // Numbered lists (1., 2., etc.)
            if (/^\d+\.\s/.test(trimmed)) {
                return (
                    <div key={i} className="flex items-start gap-4 ml-1 my-3 bg-gray-50/50 p-3 rounded-xl border border-gray-100/50">
                        <span className="flex items-center justify-center w-6 h-6 bg-green-600 text-white text-[10px] font-black rounded-lg shrink-0 shadow-sm">
                            {trimmed.match(/^(\d+)/)[1]}
                        </span>
                        <div className="text-gray-700 leading-relaxed flex-1">
                            {parts.length > 1 ? parts : trimmed.replace(/^\d+\.\s*/, '')}
                        </div>
                    </div>
                );
            }

            // Pro Tips or Practical actions
            if (trimmed.toLowerCase().includes('tip:') || trimmed.toLowerCase().includes('pro tip:')) {
                return (
                    <div key={i} className="my-5 p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-2xl border-l-4 border-emerald-500 shadow-sm">
                        <div className="flex items-center gap-2 mb-1 text-emerald-800 font-black text-xs uppercase tracking-wider">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                            Farmer Tip
                        </div>
                        <div className="text-gray-700 text-sm italic font-medium">
                            {parts.length > 1 ? parts : trimmed}
                        </div>
                    </div>
                );
            }

            // Empty line = spacer
            if (trimmed === '') {
                return <div key={i} className="h-4" />;
            }

            // Regular line
            return (
                <p key={i} className="my-2 text-gray-600 leading-[1.8] font-medium tracking-tight">
                    {parts.length > 1 ? parts : line}
                </p>
            );
        });
    }, [text]);

    return <div className="space-y-0.5">{rendered}</div>;
}

const RAGMessage = ({ msg }) => {
    const [showThinking, setShowThinking] = useState(false);

    return (
        <div className="flex justify-start animate-fade-in-up">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-green-600 to-green-800 flex items-center justify-center mr-4 mt-2 flex-shrink-0 shadow-xl shadow-green-200 border border-white/20">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
            </div>
            <div className="max-w-[88%] w-full">
                {/* Thinking Process (Sub-queries) */}
                {msg.subQueries && msg.subQueries.length > 0 && (
                    <div className="mb-4">
                        <button
                            onClick={() => setShowThinking(!showThinking)}
                            className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-gray-400 hover:text-green-600 transition-colors py-1 px-2 rounded-lg hover:bg-green-50"
                        >
                            <svg className={`w-3 h-3 transition-transform duration-300 ${showThinking ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M19 9l-7 7-7-7" />
                            </svg>
                            {showThinking ? 'Hide Thinking Process' : 'Show Thinking Process'}
                        </button>

                        {showThinking && (
                            <div className="mt-3 ml-2 flex flex-col gap-2 relative pl-6 border-l-2 border-dashed border-gray-200 py-1">
                                {msg.subQueries.map((q, idx) => (
                                    <div key={idx} className="relative group">
                                        <div className="absolute -left-[31px] top-1/2 -translate-y-1/2 w-4 h-[2px] bg-gray-200" />
                                        <div className="text-[11px] font-semibold text-gray-400 italic group-hover:text-green-500 transition-colors">
                                            "{q}"
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {/* Main Content Body */}
                <div className="bg-white text-gray-800 px-8 py-7 rounded-[32px] rounded-tl-none border border-gray-100 shadow-[0_10px_40px_-15px_rgba(0,0,0,0.05)] backdrop-blur-sm relative">
                    <FormattedMessage text={msg.text} />

                    {/* Sources / References */}
                    {msg.sources && msg.sources.length > 0 && (
                        <div className="mt-8 pt-6 border-t border-gray-100">
                            <div className="text-[9px] font-black uppercase tracking-[0.2em] text-gray-400 mb-4 flex items-center gap-2">
                                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.432.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                                </svg>
                                Reference Sources
                            </div>
                            <div className="flex flex-wrap gap-2">
                                {msg.sources.map((s, idx) => (
                                    <div key={idx} className="group flex items-center gap-2 px-3 py-1.5 bg-gray-50/50 hover:bg-green-50/50 border border-gray-100 hover:border-green-100 rounded-xl transition-all cursor-default overflow-hidden max-w-[200px]">
                                        <div className="w-4 h-4 rounded bg-green-100 flex items-center justify-center shrink-0">
                                            <span className="text-[8px] font-black text-green-700">{idx + 1}</span>
                                        </div>
                                        <div className="flex flex-col truncate">
                                            <span className="text-[10px] font-bold text-gray-700 truncate line-clamp-1">{s.name}</span>
                                            {s.pages && <span className="text-[8px] text-gray-400 font-bold">Page {s.pages}</span>}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

const ChatAssistant = ({ messages, input, setInput, handleSend, loading, scrollRef }) => {
    return (
        <div className="flex flex-col h-[calc(100vh-280px)] min-h-[600px] bg-[#fcfdfd] rounded-[40px] shadow-[0_50px_100px_-20px_rgba(0,0,0,0.08)] border border-white overflow-hidden relative">
            <div className="absolute inset-0 bg-gradient-to-b from-white to-[#f8fafc] pointer-events-none" />

            {/* Messages Area */}
            <div ref={scrollRef} className="flex-1 overflow-y-scroll p-10 space-y-10 no-scrollbar h-full relative z-10">
                {messages.map((msg) => (
                    msg.role === 'assistant' ? (
                        <RAGMessage key={msg.id} msg={msg} />
                    ) : (
                        <div key={msg.id} className="flex justify-end animate-fade-in-up">
                            <div className="max-w-[80%] px-7 py-5 bg-gradient-to-br from-gray-800 to-gray-900 text-white rounded-[28px] rounded-br-none shadow-2xl shadow-gray-200 text-[14px] font-semibold leading-relaxed tracking-tight tracking-wide border border-white/10 italic">
                                "{msg.text}"
                            </div>
                        </div>
                    )
                ))}

                {loading && (
                    <div className="flex justify-start animate-fade-in-up">
                        <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-green-600 to-green-800 flex items-center justify-center mr-4 mt-2 flex-shrink-0 shadow-xl shadow-green-200 border border-white/20">
                            <svg className="w-5 h-5 text-white animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                        </div>
                        <div className="max-w-[88%] w-full">
                            <div className="bg-white px-8 py-7 rounded-[32px] rounded-tl-none border border-gray-100 shadow-[0_10px_40px_-15px_rgba(0,0,0,0.05)]">
                                {/* Skeleton lines */}
                                <div className="space-y-3 mb-5">
                                    <div className="h-3 bg-gradient-to-r from-gray-100 via-gray-200 to-gray-100 rounded-full w-[85%] animate-pulse" style={{ animationDuration: '1.5s' }} />
                                    <div className="h-3 bg-gradient-to-r from-gray-100 via-gray-200 to-gray-100 rounded-full w-[70%] animate-pulse" style={{ animationDuration: '1.8s' }} />
                                    <div className="h-3 bg-gradient-to-r from-gray-100 via-gray-200 to-gray-100 rounded-full w-[60%] animate-pulse" style={{ animationDuration: '2.1s' }} />
                                </div>
                                {/* Typing dots */}
                                <div className="flex items-center gap-3">
                                    <div className="flex items-center gap-1.5">
                                        <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '0ms', animationDuration: '0.6s' }} />
                                        <div className="w-2 h-2 bg-green-400 rounded-full animate-bounce" style={{ animationDelay: '150ms', animationDuration: '0.6s' }} />
                                        <div className="w-2 h-2 bg-green-300 rounded-full animate-bounce" style={{ animationDelay: '300ms', animationDuration: '0.6s' }} />
                                    </div>
                                    <span className="text-[10px] font-black uppercase tracking-[0.15em] text-green-600/70 animate-pulse">
                                        Analyzing your query...
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Quick Suggestions & Input Area Container */}
            <div className="relative z-10 px-10 pb-10 pt-2 bg-white/40 backdrop-blur-xl border-t border-gray-100">
                {/* Suggestions Layer */}
                {messages.length <= 1 && !input && (
                    <div className="mb-6 flex flex-wrap gap-2.5">
                        {["Improve soil health", "Wheat fertilization", "Pest control tips", "Drip irrigation"].map((q) => (
                            <button
                                key={q}
                                onClick={() => { setInput(q); }}
                                className="text-[10px] font-black uppercase tracking-widest text-gray-500 bg-white/80 hover:bg-green-600 hover:text-white px-4 py-2.5 rounded-full border border-gray-200 shadow-sm transition-all duration-300 transform hover:-translate-y-1 active:scale-95 cursor-pointer"
                            >
                                {q}
                            </button>
                        ))}
                    </div>
                )}

                {/* Main Input Form */}
                <form onSubmit={handleSend} className="relative flex items-center gap-4 group">
                    <div className="relative flex-1">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Type your agricultural question here..."
                            className="w-full px-8 py-6 bg-white border border-gray-200 rounded-[30px] text-[15px] font-medium text-gray-800 transition-all duration-500 focus:outline-none focus:ring-[6px] focus:ring-green-500/5 focus:border-green-500 placeholder:text-gray-300 shadow-[0_10px_30px_-10px_rgba(0,0,0,0.05)]"
                        />
                        {/* Status Icon */}
                        <div className="absolute right-6 top-1/2 -translate-y-1/2 flex items-center gap-2 pointer-events-none opacity-40">
                            <div className="w-1.5 h-1.5 bg-green-500 rounded-full shadow-[0_0_10px_rgba(34,197,94,1)] animate-pulse" />
                            <span className="text-[10px] font-black uppercase tracking-widest">Active</span>
                        </div>
                    </div>
                    <button
                        type="submit"
                        disabled={!input.trim() || loading}
                        className="bg-green-600 text-white p-6 rounded-full hover:bg-green-700 transition-all duration-300 shadow-xl shadow-green-600/30 disabled:opacity-30 disabled:grayscale hover:scale-105 active:scale-95 shrink-0 group/btn cursor-pointer"
                    >
                        <svg className="w-7 h-7 group-hover/btn:translate-x-1 group-hover/btn:-translate-y-1 transition-transform duration-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                        </svg>
                    </button>
                </form>

                <div className="mt-4 text-[9px] text-center font-bold text-gray-400 uppercase tracking-[0.3em]">
                    Expert agricultural guidance powered by KrishiSaarthi Precision RAG
                </div>
            </div>
        </div>
    );
};

export default ChatAssistant;
