import { useMemo } from 'react';

/**
 * Renders a simple markdown-like message into formatted JSX.
 * Supports **bold**, bullet points (• and -), headers, and line breaks.
 */
function FormattedMessage({ text }) {
    const rendered = useMemo(() => {
        if (!text) return null;

        const lines = text.split('\n');
        return lines.map((line, i) => {
            // Bold headers (lines starting with **)
            if (line.trim().startsWith('**') && line.trim().endsWith('**')) {
                const content = line.trim().replace(/^\*\*/, '').replace(/\*\*$/, '');
                return <h4 key={i} className="font-bold text-[15px] mt-3 mb-1">{content}</h4>;
            }

            // Inline bold conversion
            let formatted = line;
            const parts = [];
            const regex = /\*\*(.*?)\*\*/g;
            let lastIndex = 0;
            let match;

            while ((match = regex.exec(formatted)) !== null) {
                if (match.index > lastIndex) {
                    parts.push(<span key={`${i}-${lastIndex}`}>{formatted.slice(lastIndex, match.index)}</span>);
                }
                parts.push(<strong key={`${i}-b-${match.index}`} className="font-bold">{match[1]}</strong>);
                lastIndex = regex.lastIndex;
            }
            if (lastIndex < formatted.length) {
                parts.push(<span key={`${i}-end`}>{formatted.slice(lastIndex)}</span>);
            }

            // Bullet points
            const trimmed = line.trim();
            if (trimmed.startsWith('•') || trimmed.startsWith('-') || trimmed.startsWith('*') && !trimmed.startsWith('**')) {
                const bulletContent = trimmed.replace(/^[•\-\*]\s*/, '');
                return (
                    <div key={i} className="flex items-start gap-2 ml-2 my-0.5">
                        <span className="text-green-500 mt-0.5 flex-shrink-0">•</span>
                        <span>{parts.length > 1 ? parts : bulletContent}</span>
                    </div>
                );
            }

            // Numbered lists (1., 2., etc.)
            if (/^\d+\.\s/.test(trimmed)) {
                return (
                    <div key={i} className="flex items-start gap-2 ml-2 my-0.5">
                        <span className="text-green-600 font-bold flex-shrink-0">{trimmed.match(/^(\d+)/)[1]}.</span>
                        <span>{parts.length > 1 ? parts : trimmed.replace(/^\d+\.\s*/, '')}</span>
                    </div>
                );
            }

            // Table rows (basic support)
            if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
                if (trimmed.includes('---')) return null; // Skip separator rows
                return (
                    <div key={i} className="text-xs font-mono bg-gray-50 px-2 py-0.5 rounded">
                        {trimmed}
                    </div>
                );
            }

            // Empty line = spacer
            if (trimmed === '') {
                return <div key={i} className="h-2" />;
            }

            // Regular line with possible inline bold
            return <p key={i} className="my-0.5">{parts.length > 1 ? parts : line}</p>;
        });
    }, [text]);

    return <div className="space-y-0">{rendered}</div>;
}

const ChatAssistant = ({ messages, input, setInput, handleSend, loading, scrollRef }) => {
    return (
        <div className="flex flex-col h-[calc(100vh-280px)] min-h-[550px] bg-white/80 backdrop-blur-xl rounded-[32px] shadow-2xl shadow-green-900/5 border border-white overflow-hidden">
            {/* Messages Area */}
            <div ref={scrollRef} className="flex-1 overflow-y-auto p-8 space-y-6 no-scrollbar h-full">
                {messages.map((msg) => (
                    <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}>
                        {msg.role === 'assistant' && (
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-green-500 to-green-700 flex items-center justify-center mr-3 mt-1 flex-shrink-0 shadow-md">
                                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9l-.707.707M12 18a6 6 0 100-12 6 6 0 000 12z" />
                                </svg>
                            </div>
                        )}
                        <div className={`max-w-[85%] px-6 py-4 rounded-3xl text-[14px] leading-relaxed shadow-sm ${msg.role === 'user'
                            ? 'bg-gradient-to-br from-green-600 to-green-700 text-white rounded-br-none'
                            : 'bg-white text-gray-800 rounded-bl-none border border-gray-100'
                            }`}>
                            {msg.role === 'assistant' ? (
                                <FormattedMessage text={msg.text} />
                            ) : (
                                msg.text
                            )}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex justify-start">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-green-500 to-green-700 flex items-center justify-center mr-3 flex-shrink-0 shadow-md">
                            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9l-.707.707M12 18a6 6 0 100-12 6 6 0 000 12z" />
                            </svg>
                        </div>
                        <div className="bg-white border border-gray-100 px-6 py-4 rounded-3xl rounded-bl-none flex gap-1.5 shadow-sm">
                            <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" />
                            <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce [animation-delay:0.2s]" />
                            <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce [animation-delay:0.4s]" />
                        </div>
                    </div>
                )}
            </div>

            {/* Quick Suggestions */}
            {messages.length <= 1 && (
                <div className="px-6 pb-2 flex flex-wrap gap-2">
                    {["How to improve soil health?", "Best fertilizer for wheat?", "Pest control for rice", "Drip irrigation setup"].map((q) => (
                        <button
                            key={q}
                            onClick={() => { setInput(q); }}
                            className="text-xs font-medium text-gray-500 bg-gray-50 hover:bg-green-50 hover:text-green-700 px-3 py-1.5 rounded-full border border-gray-100 hover:border-green-200 transition-all cursor-pointer"
                        >
                            {q}
                        </button>
                    ))}
                </div>
            )}

            {/* Input Area */}
            <div className="p-6 bg-gray-50/50 backdrop-blur-sm border-t border-gray-100">
                <form onSubmit={handleSend} className="relative flex gap-4">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask about soil health, pest control, fertilizers, or crop management..."
                        className="flex-1 px-7 py-4 bg-white border border-gray-100 rounded-[22px] text-sm focus:outline-none focus:ring-4 focus:ring-green-500/10 focus:border-green-500 transition-all shadow-inner"
                    />
                    <button
                        type="submit"
                        disabled={!input.trim() || loading}
                        className="bg-green-600 text-white p-4 rounded-[22px] hover:bg-green-700 transition-all shadow-xl shadow-green-600/30 disabled:opacity-50 disabled:cursor-not-allowed group cursor-pointer"
                    >
                        <svg className="w-6 h-6 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                        </svg>
                    </button>
                </form>
            </div>
        </div>
    );
};

export default ChatAssistant;
