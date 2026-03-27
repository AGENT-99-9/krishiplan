import Navbar from '../components/Navbar';
import Hero from '../components/Hero';
import Footer from '../components/Footer';
import Button from '../components/Button';

export default function LandingPage() {
    return (
        <div className="min-h-screen flex flex-col bg-slate-50">
            <Navbar />
            <main className="flex-1">
                <Hero />

                {/* ── Features Section ─────────────────────── */}
                <section className="py-24 bg-white relative overflow-hidden">
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                        <div className="text-center mb-16">
                            <span className="inline-block px-4 py-1.5 mb-4 text-xs font-bold uppercase tracking-widest text-krishi-700 bg-krishi-100/50 rounded-full border border-krishi-200">
                                Complete Platform
                            </span>
                            <h2 className="text-3xl font-bold text-gray-900 sm:text-4xl">
                                Everything you need to succeed
                            </h2>
                            <p className="mt-4 text-lg text-gray-500 max-w-2xl mx-auto">
                                A comprehensive ecosystem built specifically for the modern Indian farmer.
                            </p>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
                            {[
                                {
                                    title: "AI-Powered Fertilizer Advisor",
                                    desc: "Upload soil photos or lab reports, get ML-driven fertilizer recommendations with exact dosage calculations using our LightGBM model.",
                                    icon: (
                                        <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19 14.5M14.25 3.104c.251.023.501.05.75.082M19 14.5l-2.47 2.47a2.25 2.25 0 01-1.591.659H9.061a2.25 2.25 0 01-1.591-.659L5 14.5m14 0V17a2.25 2.25 0 01-2.25 2.25H7.25A2.25 2.25 0 015 17v-2.5" />
                                        </svg>
                                    ),
                                    color: "bg-blue-50 text-blue-600",
                                    features: ["Soil Photo Analysis", "Lab Report OCR", "N-P-K Dosage"]
                                },
                                {
                                    title: "Direct Marketplace",
                                    desc: "Buy seeds, fertilizers, and equipment directly from verified sellers. No middlemen, competitive prices, order tracking.",
                                    icon: (
                                        <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M2.25 3h1.386c.51 0 .955.343 1.087.835l.383 1.437M7.5 14.25a3 3 0 00-3 3h15.75m-12.75-3h11.218c1.121-2.3 2.1-4.684 2.924-7.138a60.114 60.114 0 00-16.536-1.84M7.5 14.25L5.106 5.272M6 20.25a.75.75 0 11-1.5 0 .75.75 0 011.5 0zm12.75 0a.75.75 0 11-1.5 0 .75.75 0 011.5 0z" />
                                        </svg>
                                    ),
                                    color: "bg-krishi-50 text-krishi-600",
                                    features: ["Buy & Sell", "Order Tracking", "Category Filters"]
                                },
                                {
                                    title: "Farmer Community",
                                    desc: "Connect with thousands of experts and peers. Share knowledge, discuss challenges, and get peer-reviewed agricultural advice.",
                                    icon: (
                                        <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
                                        </svg>
                                    ),
                                    color: "bg-orange-50 text-orange-600",
                                    features: ["Discussions", "Expert Advice", "Topic Categories"]
                                }
                            ].map((feature, idx) => (
                                <div key={idx} className="group p-8 rounded-3xl border border-gray-100 bg-white hover:border-krishi-200 hover:shadow-xl hover:shadow-krishi-500/5 transition-all duration-300">
                                    <div className={`w-14 h-14 ${feature.color} rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}>
                                        {feature.icon}
                                    </div>
                                    <h3 className="text-xl font-bold text-gray-900 mb-3">{feature.title}</h3>
                                    <p className="text-gray-500 leading-relaxed mb-5">{feature.desc}</p>
                                    <div className="flex flex-wrap gap-2">
                                        {feature.features.map((f) => (
                                            <span key={f} className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full bg-gray-50 text-gray-500 border border-gray-100">
                                                {f}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </section>

                {/* ── How It Works Section ──────────────────── */}
                <section className="py-24 bg-gray-50/50">
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                        <div className="text-center mb-16">
                            <h2 className="text-3xl font-bold text-gray-900 sm:text-4xl">How KrishiSaarthi Works</h2>
                            <p className="mt-4 text-lg text-gray-500 max-w-2xl mx-auto">From soil to harvest — get intelligent guidance at every step</p>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                            {[
                                { step: "01", title: "Upload Soil Data", desc: "Take a photo of your soil or upload a lab report for instant analysis.", icon: "📷" },
                                { step: "02", title: "Get AI Analysis", desc: "Our ML model analyzes N-P-K levels and recommends the right fertilizer.", icon: "🧠" },
                                { step: "03", title: "Buy Supplies", desc: "Purchase recommended fertilizers directly from our marketplace.", icon: "🛒" },
                                { step: "04", title: "Track & Grow", desc: "Monitor your orders, track results, and connect with the community.", icon: "📈" }
                            ].map((item) => (
                                <div key={item.step} className="relative text-center">
                                    <div className="text-4xl mb-4">{item.icon}</div>
                                    <span className="text-xs font-black text-krishi-500 uppercase tracking-widest">Step {item.step}</span>
                                    <h3 className="text-lg font-bold text-gray-900 mt-2 mb-2">{item.title}</h3>
                                    <p className="text-sm text-gray-500">{item.desc}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </section>

                {/* ── Tech Stack / Trust ────────────────────── */}
                <section className="py-16 bg-white border-t border-gray-100">
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                        <p className="text-center text-sm text-gray-400 uppercase tracking-widest font-bold mb-8">Powered By</p>
                        <div className="flex flex-wrap items-center justify-center gap-x-12 gap-y-6">
                            {["React 19", "Django REST", "MongoDB Atlas", "LightGBM ML", "Tesseract OCR", "TailwindCSS 4"].map((tech) => (
                                <span key={tech} className="text-gray-400 font-bold text-sm hover:text-gray-600 transition-colors">
                                    {tech}
                                </span>
                            ))}
                        </div>
                    </div>
                </section>

                {/* ── Impact / CTA Section ──────────────────── */}
                <section className="py-24 bg-gradient-to-b from-white to-krishi-50/30">
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                        <div className="bg-krishi-900 rounded-[3rem] overflow-hidden relative shadow-2xl shadow-krishi-900/20">
                            <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-10" />
                            <div className="relative px-8 py-20 sm:px-16 sm:py-24 text-center">
                                <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
                                    Ready to modernize your farm?
                                </h2>
                                <p className="text-krishi-100 text-lg mb-10 max-w-2xl mx-auto leading-relaxed">
                                    Join farmers who are already using KrishiSaarthi to increase their yield and efficiency with AI-powered insights.
                                </p>
                                <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                                    <Button to="/signup" variant="primary" className="bg-white text-krishi-900 hover:bg-krishi-50 border-none scale-110">
                                        Get Started Free&nbsp;&nbsp;→
                                    </Button>
                                    <p className="text-krishi-400 text-sm sm:ml-4 flex items-center gap-2">
                                        <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse" />
                                        Free forever • No credit card required
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
            </main>
            <Footer />
        </div>
    );
}
