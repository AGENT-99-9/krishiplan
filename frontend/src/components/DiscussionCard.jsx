import { formatRelativeTime } from '../utils/time';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import communityApi from '../api/communityApi';

export default function DiscussionCard({ post, onInteraction }) {
    const navigate = useNavigate();
    const [showComments, setShowComments] = useState(false);
    const [commentText, setCommentText] = useState('');

    const checkAuth = () => {
        if (!localStorage.getItem('access_token')) {
            alert('Please log in to participate in the community.');
            navigate('/login');
            return false;
        }
        return true;
    };

    const handleLike = async () => {
        if (!checkAuth()) return;
        try {
            await communityApi.likePost(post.id);
            onInteraction();
        } catch (err) {
            console.error('Like error:', err);
        }
    };

    const handleComment = async (e) => {
        e.preventDefault();
        if (!checkAuth() || !commentText.trim()) return;
        try {
            await communityApi.createComment(post.id, commentText);
            setCommentText('');
            onInteraction();
        } catch (err) {
            console.error('Comment error:', err);
        }
    };

    const timeAgo = post.created_at ? formatRelativeTime(post.created_at) : 'some time ago';
    const initial = (post.author_name || 'A')[0].toUpperCase();

    return (
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100 hover:shadow-md transition-shadow">
            {/* Author Info */}
            <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-krishi-500 to-krishi-700 flex items-center justify-center text-white font-bold text-lg shadow-sm">
                    {initial}
                </div>
                <div>
                    <h4 className="text-sm font-bold text-gray-900 leading-none">{post.author_name}</h4>
                    <p className="text-xs text-gray-400 mt-1">{timeAgo}</p>
                </div>
                <div className="ml-auto">
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded bg-gray-50 text-gray-500 border border-gray-100">
                        {post.category}
                    </span>
                </div>
            </div>

            {/* Content */}
            <div className="mb-6">
                <h3 className="text-lg font-bold text-gray-900 mb-2">{post.title}</h3>
                <p className="text-sm text-gray-600 leading-relaxed whitespace-pre-wrap">
                    {post.description}
                </p>
            </div>

            {/* Interaction Bar */}
            <div className="flex items-center gap-6 pt-4 border-t border-gray-50">
                <button
                    onClick={handleLike}
                    className="flex items-center gap-2 text-sm font-medium text-gray-600 hover:text-red-500 transition-colors group cursor-pointer"
                >
                    <span className="text-lg group-active:scale-125 transition-transform">❤️</span>
                    {post.like_count}
                </button>
                <button
                    onClick={() => setShowComments(!showComments)}
                    className="flex items-center gap-2 text-sm font-medium text-gray-600 hover:text-krishi-600 transition-colors group cursor-pointer"
                >
                    <span className="text-lg group-active:scale-125 transition-transform">💬</span>
                    {post.comment_count}
                </button>
            </div>

            {/* Comments Section */}
            {showComments && (
                <div className="mt-6 space-y-4 animate-fade-in">
                    <div className="space-y-3">
                        {post.comments?.map((c) => (
                            <div key={c.id} className="bg-gray-50 rounded-xl p-3 text-sm">
                                <span className="font-bold text-gray-900">{c.user_name}</span>
                                <p className="text-gray-600 mt-1">{c.text}</p>
                            </div>
                        ))}
                    </div>
                    <form onSubmit={handleComment} className="flex gap-2">
                        <input
                            type="text"
                            placeholder="Write a comment..."
                            value={commentText}
                            onChange={(e) => setCommentText(e.target.value)}
                            className="flex-1 bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-krishi-500/20"
                        />
                        <button
                            type="submit"
                            className="bg-krishi-600 text-white text-xs font-bold px-4 py-2 rounded-lg hover:bg-krishi-700 transition-colors cursor-pointer"
                        >
                            Post
                        </button>
                    </form>
                </div>
            )}
        </div>
    );
}
