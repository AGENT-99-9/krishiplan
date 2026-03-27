export default function ProfileCard({ user }) {
    const initial = (user?.username || user?.email || 'U').charAt(0).toUpperCase();
    const displayName = user?.full_name || user?.username || 'User';
    const displayEmail = user?.email || '';

    return (
        <div className="flex flex-col items-center py-6 px-4 border-b border-gray-100">
            {/* Avatar */}
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-krishi-500 to-krishi-700 flex items-center justify-center shadow-lg shadow-krishi-500/20 mb-3">
                <span className="text-2xl font-bold text-white">{initial}</span>
            </div>

            {/* Name & Email */}
            <h3 className="text-base font-semibold text-gray-900 text-center">
                {displayName}
            </h3>
            <p className="text-sm text-gray-500 mt-0.5 text-center truncate max-w-full">
                {displayEmail}
            </p>
        </div>
    );
}
