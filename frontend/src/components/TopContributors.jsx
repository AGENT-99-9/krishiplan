export default function TopContributors({ contributors }) {
    return (
        <div className="bg-white rounded-xl shadow p-6 border border-gray-100">
            <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider mb-4 flex items-center gap-2">
                <span>🏆</span> Top Contributors
            </h3>
            <div className="space-y-5">
                {contributors.map((user, idx) => (
                    <div key={idx} className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-full bg-krishi-100 flex items-center justify-center text-krishi-700 font-bold text-sm border border-krishi-200">
                            {(user.full_name || user.username || 'U')[0].toUpperCase()}
                        </div>
                        <div className="flex-1 min-w-0">
                            <h4 className="text-sm font-bold text-gray-900 truncate">
                                {user.full_name || user.username}
                            </h4>
                            <p className="text-[11px] text-gray-400">{user.role}</p>
                        </div>
                        <div className="text-right">
                            <span className="text-sm font-bold text-krishi-600">{user.points}</span>
                            <span className="text-[10px] text-gray-400 block -mt-1 font-medium">pt</span>
                        </div>
                    </div>
                ))}
                {contributors.length === 0 && (
                    <p className="text-xs text-gray-400 italic">No contributors yet</p>
                )}
            </div>
        </div>
    );
}
