export default function CommunityHeader({ onOpenModal }) {
    return (
        <div className="bg-krishi-50 rounded-2xl p-8 mb-8 flex flex-col md:flex-row items-center justify-between shadow-sm border border-krishi-100">
            <div className="mb-6 md:mb-0">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">Farmer Community</h1>
                <p className="text-gray-600 max-w-xl text-lg">
                    Connect with fellow farmers and agriculture experts. Share knowledge, ask questions, and grow together.
                </p>
            </div>
            <div>
                <button
                    onClick={onOpenModal}
                    className="bg-krishi-600 text-white rounded-full px-8 py-3 font-semibold hover:bg-krishi-700 transition shadow-lg shadow-krishi-500/25 cursor-pointer whitespace-nowrap"
                >
                    Ask Question
                </button>
            </div>
        </div>
    );
}
