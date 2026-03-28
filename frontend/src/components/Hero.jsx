import Button from './Button';

export default function Hero() {
    const userStr = localStorage.getItem('user');
    const user = userStr ? JSON.parse(userStr) : null;
    const isVendor = user?.role === 'vendor';

    return (
        <section className="relative min-h-[calc(100vh-4rem)] flex items-center justify-center overflow-hidden">
            {/* ── Background Gradient ────────────────────── */}
            <div className="absolute inset-0 bg-gradient-to-br from-krishi-50 via-white to-krishi-100/60" />

            {/* ── Decorative Leaf Shapes ─────────────────── */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <svg
                    className={`absolute -top-20 -right-20 w-[500px] h-[500px] ${isVendor ? 'text-blue-200/30' : 'text-krishi-200/30'} animate-float`}
                    viewBox="0 0 200 200"
                    fill="currentColor"
                >
                    <path d="M100 10c-30 0-60 20-75 50-20 40-10 90 25 120 10 10 30 15 50 15s40-5 50-15c35-30 45-80 25-120C160 30 130 10 100 10z" />
                </svg>

                <svg
                    className={`absolute -bottom-32 -left-24 w-[400px] h-[400px] ${isVendor ? 'text-blue-100/50' : 'text-krishi-100/50'} animate-pulse-soft`}
                    viewBox="0 0 200 200"
                    fill="currentColor"
                >
                    <path d="M100 10c-30 0-60 20-75 50-20 40-10 90 25 120 10 10 30 15 50 15s40-5 50-15c35-30 45-80 25-120C160 30 130 10 100 10z" />
                </svg>
            </div>

            {/* ── Content ────────────────────────────────── */}
            <div className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center py-20">
                {/* Badge */}
                <div className={`animate-fade-in-up inline-flex items-center gap-2 px-4 py-2 mb-8 rounded-full border backdrop-blur-sm ${isVendor ? 'bg-blue-100/80 border-blue-200/60' : 'bg-krishi-100/80 border-krishi-200/60'}`}>
                    <span className={`w-2 h-2 rounded-full animate-pulse ${isVendor ? 'bg-blue-500' : 'bg-krishi-500'}`} />
                    <span className={`text-sm font-medium ${isVendor ? 'text-blue-700' : 'text-krishi-700'}`}>
                        {isVendor ? 'Enterprise Business Portal' : 'AI-Powered Agriculture Platform'}
                    </span>
                </div>

                {/* Headline */}
                <h1 className="animate-fade-in-up text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-tight">
                    <span className="text-gray-900">{isVendor ? 'Empowering Agri-Business with' : 'Empowering Agriculture with'}</span>
                    <br />
                    <span className={`bg-gradient-to-r ${isVendor ? 'from-blue-600 to-blue-400' : 'from-krishi-600 to-krishi-400'} bg-clip-text text-transparent`}>
                        {isVendor ? 'Smart Supply Chains' : 'Intelligent Insights'}
                    </span>
                </h1>

                {/* Subtitle */}
                <p className="animate-fade-in-up-delay mt-6 text-lg sm:text-xl text-gray-500 max-w-2xl mx-auto leading-relaxed">
                    {isVendor
                        ? 'KrishiSaarthi provides vendors with advanced inventory management, logistic tracking, and deep sales analytics to reach farmers everywhere.'
                        : 'KrishiSaarthi combines cutting-edge AI with a robust marketplace and community to help you yield more, sustainably.'}
                </p>

                {/* CTA Buttons */}
                <div className="animate-fade-in-up-delay-2 mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
                    {isVendor ? (
                        <>
                            <Button to="/vendor-dashboard" variant="primary" className="bg-blue-600 hover:bg-blue-700">
                                Launch Business Suite&nbsp;&nbsp;→
                            </Button>
                            <Button to="/vendor-dashboard" variant="secondary">
                                View Inventory
                            </Button>
                        </>
                    ) : (
                        <>
                            <Button to="/assistant" variant="primary">
                                Try AI Assistant&nbsp;&nbsp;→
                            </Button>
                            <Button to="/marketplace" variant="secondary">
                                Browse Marketplace
                            </Button>
                        </>
                    )}
                </div>

                {/* Stats */}
                <div className="animate-fade-in-up-delay-2 mt-16 grid grid-cols-3 gap-8 max-w-lg mx-auto">
                    {[
                        { value: isVendor ? '₹1M+' : '10K+', label: isVendor ? 'Potential Revenue' : 'Farmers' },
                        { value: isVendor ? '24/7' : '500+', label: isVendor ? 'Stock Monitoring' : 'Products' },
                        { value: '99.9%', label: 'Cloud Uptime' },
                    ].map((stat) => (
                        <div key={stat.label} className="text-center">
                            <p className="text-2xl sm:text-3xl font-bold text-gray-800">
                                {stat.value}
                            </p>
                            <p className="text-sm text-gray-400 mt-1">{stat.label}</p>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
