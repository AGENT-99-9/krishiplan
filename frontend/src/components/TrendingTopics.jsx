export default function TrendingTopics({ topics }) {
    return (
        <div className="bg-white rounded-xl shadow p-6 border border-gray-100">
            <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider mb-4 flex items-center gap-2">
                <span>🔥</span> Trending Topics
            </h3>
            <div className="space-y-4">
                {topics.map((topic, idx) => (
                    <div key={idx} className="group cursor-pointer">
                        <h4 className="text-sm font-bold text-gray-800 group-hover:text-krishi-600 transition-colors line-clamp-1">
                            {topic.title}
                        </h4>
                        <p className="text-[11px] text-gray-400 mt-0.5">{topic.reply_count} replies</p>
                    </div>
                ))}
                {topics.length === 0 && (
                    <p className="text-xs text-gray-400 italic">No trending topics yet</p>
                )}
            </div>
        </div>
    );
}
