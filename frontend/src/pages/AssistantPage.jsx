import { useState, useRef, useEffect } from 'react';
import DashboardNavbar from '../components/DashboardNavbar';
import Footer from '../components/Footer';
import assistantApi from '../api/assistantApi';
import ChatAssistant from '../components/ChatAssistant';
import FertilizerAdvisor from '../components/FertilizerAdvisor';

export default function AssistantPage() {
    const [activeTab, setActiveTab] = useState('chat'); // 'chat' or 'fertilizer'
    const [messages, setMessages] = useState([
        { id: 1, role: 'assistant', text: "Hello! I'm your KrishiSaarthi AI assistant. How can I help you with your farming today?" }
    ]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const scrollRef = useRef(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, activeTab]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim() || loading) return;

        const userMsg = { id: Date.now(), role: 'user', text: input };
        setMessages(prev => [...prev, userMsg]);
        setInput("");
        setLoading(true);

        try {
            const data = await assistantApi.askQuestion(input);
            const aiMsg = { id: Date.now() + 1, role: 'assistant', text: data.response };
            setMessages(prev => [...prev, aiMsg]);
        } catch (err) {
            console.error('Assistant error:', err);
            setMessages(prev => [...prev, { id: Date.now() + 1, role: 'assistant', text: "Sorry, I'm having trouble connecting right now. Please try again later." }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex flex-col bg-[#fcfdfd]">
            {/* Ambient Background Elements */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-[-10%] right-[-10%] w-[40%] h-[40%] bg-green-50 rounded-full blur-[120px] opacity-60"></div>
                <div className="absolute bottom-[-10%] left-[-10%] w-[30%] h-[30%] bg-blue-50 rounded-full blur-[100px] opacity-40"></div>
            </div>

            <DashboardNavbar />

            <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-10 relative z-10">
                {/* Header Section */}
                <div className="mb-12 text-center animate-fade-in-up">
                    <span className="inline-block px-4 py-1.5 mb-4 text-xs font-bold uppercase tracking-widest text-green-700 bg-green-100/50 rounded-full border border-green-200">
                        Intelligent Agriculture
                    </span>
                    <h1 className="text-4xl md:text-5xl font-black text-gray-900 tracking-tight mb-4">
                        AI <span className="bg-gradient-to-r from-green-600 to-green-500 bg-clip-text text-transparent">Assistant Hub</span>
                    </h1>
                    <p className="text-lg text-gray-500 max-w-2xl mx-auto leading-relaxed">
                        Harness the power of machine learning to optimize your farm. Instant expert chat and data-driven fertilizer recommendations.
                    </p>
                </div>

                {/* Modern Segmented Control */}
                <div className="flex justify-center mb-12">
                    <div className="bg-white/70 backdrop-blur-md p-1.5 rounded-[22px] shadow-2xl shadow-gray-200/50 border border-white/50 flex gap-1 items-center">
                        <button
                            onClick={() => setActiveTab('chat')}
                            className={`flex items-center gap-2.5 px-8 py-3.5 rounded-[18px] text-sm font-bold transition-all duration-500 ${activeTab === 'chat'
                                ? 'bg-green-600 text-white shadow-xl shadow-green-200 ring-1 ring-green-600'
                                : 'text-gray-500 hover:text-green-600 hover:bg-white'}`}
                        >
                            <svg className="w-5 h-5 transition-transform group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                            </svg>
                            Expert Chat
                        </button>
                        <button
                            onClick={() => setActiveTab('fertilizer')}
                            className={`flex items-center gap-2.5 px-8 py-3.5 rounded-[18px] text-sm font-bold transition-all duration-500 ${activeTab === 'fertilizer'
                                ? 'bg-green-600 text-white shadow-xl shadow-green-200 ring-1 ring-green-600'
                                : 'text-gray-500 hover:text-green-600 hover:bg-white'}`}
                        >
                            <svg className="w-5 h-5 transition-transform group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                            </svg>
                            Fertilizer Advisor
                        </button>
                    </div>
                </div>

                {/* Main Content Hub */}
                <div className="max-w-6xl mx-auto transition-all duration-700">
                    {activeTab === 'chat' ? (
                        <div className="max-w-3xl mx-auto w-full animate-fade-in-up">
                            <ChatAssistant
                                messages={messages}
                                input={input}
                                setInput={setInput}
                                handleSend={handleSend}
                                loading={loading}
                                scrollRef={scrollRef}
                            />
                        </div>
                    ) : (
                        <div className="animate-fade-in-up">
                            <FertilizerAdvisor />
                        </div>
                    )}
                </div>
            </main>

            <Footer />
        </div>
    );
}
