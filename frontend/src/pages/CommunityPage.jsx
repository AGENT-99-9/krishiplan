import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import DashboardNavbar from '../components/DashboardNavbar';
import Footer from '../components/Footer';
import CommunitySidebar from '../components/CommunitySidebar';
import DiscussionCard from '../components/DiscussionCard';
import TrendingTopics from '../components/TrendingTopics';
import TopContributors from '../components/TopContributors';
import communityApi from '../api/communityApi';
import AskQuestionModal from '../components/AskQuestionModal';

export default function CommunityPage() {
    const navigate = useNavigate();
    const [posts, setPosts] = useState([]);
    const [trending, setTrending] = useState([]);
    const [contributors, setContributors] = useState([]);
    const [category, setCategory] = useState('All Discussions');
    const [search, setSearch] = useState('');
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);

    const loadData = useCallback(async () => {
        try {
            const [postsData, trendingData, contributorsData] = await Promise.all([
                communityApi.fetchPosts({ category, search }),
                communityApi.fetchTrending(),
                communityApi.fetchContributors()
            ]);
            setPosts(postsData);
            setTrending(trendingData);
            setContributors(contributorsData);
        } catch (err) {
            console.error('Error loading community data:', err);
        } finally {
            setLoading(false);
        }
    }, [category, search]);

    useEffect(() => {
        try {
            const raw = localStorage.getItem('user');
            const user = raw ? JSON.parse(raw) : null;
            if (user && user.role === 'vendor') {
                navigate('/vendor-dashboard');
                return;
            }
        } catch { /* ignore malformed user */ }
        loadData();
    }, [loadData, navigate]);

    return (
        <div className="min-h-screen flex flex-col bg-gray-50/50">
            <DashboardNavbar />

            <main className="flex-1 max-w-[1440px] mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
                {/* Three-Column Layout */}
                <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr_320px] gap-8">

                    {/* Left Sidebar */}
                    <CommunitySidebar
                        activeCategory={category}
                        onCategoryChange={setCategory}
                        onSearch={setSearch}
                    />

                    {/* Center Discussion Feed */}
                    <div className="space-y-6">
                        {/* Header with Search/Create Action */}
                        <div className="flex items-center justify-between mb-2">
                            <div>
                                <h1 className="text-2xl font-bold text-gray-900">{category}</h1>
                                <p className="text-sm text-gray-500">{posts.length} discussions found</p>
                            </div>
                            <button
                                onClick={() => {
                                    if (!localStorage.getItem('access_token')) {
                                        alert('Please log in to start a discussion.');
                                        window.location.href = '/login';
                                        return;
                                    }
                                    setIsModalOpen(true);
                                }}
                                className="bg-krishi-600 text-white font-bold text-sm px-6 py-2.5 rounded-full hover:bg-krishi-700 transition-all shadow-lg shadow-krishi-600/20 active:scale-95 cursor-pointer"
                            >
                                Start Discussion
                            </button>
                        </div>

                        {loading ? (
                            <div className="grid gap-6">
                                {[1, 2, 3].map(i => (
                                    <div key={i} className="bg-white rounded-xl h-48 animate-pulse shadow-sm border border-gray-100" />
                                ))}
                            </div>
                        ) : (
                            <div className="grid gap-6">
                                {posts.map((post) => (
                                    <DiscussionCard
                                        key={post.id}
                                        post={post}
                                        onInteraction={loadData}
                                    />
                                ))}
                                {posts.length === 0 && (
                                    <div className="text-center py-20 bg-white rounded-2xl border border-dashed border-gray-200">
                                        <p className="text-gray-400 font-medium">No discussions match your criteria.</p>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>

                    {/* Right Sidebar */}
                    <div className="space-y-8">
                        <TrendingTopics topics={trending} />
                        <TopContributors contributors={contributors} />
                    </div>
                </div>
            </main>

            <Footer />

            {/* Modal for creating posts */}
            <AskQuestionModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onCreated={loadData}
                category={category === 'All Discussions' ? 'Crop Management' : category}
            />
        </div>
    );
}
