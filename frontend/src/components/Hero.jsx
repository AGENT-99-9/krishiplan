import Button from './Button';

export default function Hero() {
    return (
        <section className="relative min-h-[calc(100vh-4rem)] flex items-center justify-center overflow-hidden">
            {/* ── Background Gradient ────────────────────── */}
            <div className="absolute inset-0 bg-gradient-to-br from-krishi-50 via-white to-krishi-100/60" />

            {/* ── Decorative Leaf Shapes ─────────────────── */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                {/* Top-right leaf */}
                <svg
                    className="absolute -top-20 -right-20 w-[500px] h-[500px] text-krishi-200/30 animate-float"
                    viewBox="0 0 200 200"
                    fill="currentColor"
                >
                    <path d="M100 10c-30 0-60 20-75 50-20 40-10 90 25 120 10 10 30 15 50 15s40-5 50-15c35-30 45-80 25-120C160 30 130 10 100 10z" />
                </svg>

                {/* Bottom-left leaf */}
                <svg
                    className="absolute -bottom-32 -left-24 w-[400px] h-[400px] text-krishi-100/50 animate-pulse-soft"
                    viewBox="0 0 200 200"
                    fill="currentColor"
                >
                    <path d="M100 10c-30 0-60 20-75 50-20 40-10 90 25 120 10 10 30 15 50 15s40-5 50-15c35-30 45-80 25-120C160 30 130 10 100 10z" />
                </svg>

                {/* Subtle dots pattern */}
                <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-krishi-300/40 rounded-full" />
                <div className="absolute top-1/3 right-1/3 w-3 h-3 bg-krishi-200/30 rounded-full" />
                <div className="absolute bottom-1/4 right-1/4 w-2 h-2 bg-krishi-400/20 rounded-full" />
            </div>

            {/* ── Content ────────────────────────────────── */}
            <div className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center py-20">
                {/* Badge */}
                <div className="animate-fade-in-up inline-flex items-center gap-2 px-4 py-2 mb-8 rounded-full bg-krishi-100/80 border border-krishi-200/60 backdrop-blur-sm">
                    <span className="w-2 h-2 bg-krishi-500 rounded-full animate-pulse" />
                    <span className="text-sm font-medium text-krishi-700">
                        AI-Powered Agriculture Platform
                    </span>
                </div>

                {/* Headline */}
                <h1 className="animate-fade-in-up text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-tight">
                    <span className="text-gray-900">Empowering Agriculture with</span>
                    <br />
                    <span className="bg-gradient-to-r from-krishi-600 to-krishi-400 bg-clip-text text-transparent">
                        Intelligent Insights
                    </span>
                </h1>

                {/* Subtitle */}
                <p className="animate-fade-in-up-delay mt-6 text-lg sm:text-xl text-gray-500 max-w-2xl mx-auto leading-relaxed">
                    KrishiSaarthi combines cutting-edge AI with a robust marketplace and
                    community to help you yield more, sustainably.
                </p>

                {/* CTA Buttons */}
                <div className="animate-fade-in-up-delay-2 mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
                    <Button to="/assistant" variant="primary">
                        Try AI Assistant&nbsp;&nbsp;→
                    </Button>
                    <Button to="/marketplace" variant="secondary">
                        Browse Marketplace
                    </Button>
                </div>

                {/* Stats */}
                <div className="animate-fade-in-up-delay-2 mt-16 grid grid-cols-3 gap-8 max-w-lg mx-auto">
                    {[
                        { value: '10K+', label: 'Farmers' },
                        { value: '500+', label: 'Products' },
                        { value: '99%', label: 'Uptime' },
                    ].map((stat) => (
                        <div key={stat.label} className="text-center">
                            <p className="text-2xl sm:text-3xl font-bold text-krishi-600">
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
