export default function StatCard({ title, value, icon, color = 'krishi' }) {
    const colorMap = {
        krishi: {
            bg: 'bg-krishi-50',
            text: 'text-krishi-600',
            iconBg: 'bg-krishi-100',
        },
        blue: {
            bg: 'bg-blue-50',
            text: 'text-blue-600',
            iconBg: 'bg-blue-100',
        },
        purple: {
            bg: 'bg-purple-50',
            text: 'text-purple-600',
            iconBg: 'bg-purple-100',
        },
    };

    const scheme = colorMap[color] || colorMap.krishi;

    return (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow duration-300 group">
            <div className="flex items-start justify-between">
                <div>
                    <p className="text-sm font-medium text-gray-500 mb-1">{title}</p>
                    <p className="text-3xl font-bold text-gray-900">{value}</p>
                </div>
                <div
                    className={`w-12 h-12 ${scheme.iconBg} rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300`}
                >
                    <span className={scheme.text}>{icon}</span>
                </div>
            </div>
        </div>
    );
}
