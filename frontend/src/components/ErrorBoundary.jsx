import React from 'react';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        console.error("Uncaught error:", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 px-4 text-center">
                    <div className="w-20 h-20 bg-red-100 rounded-3xl flex items-center justify-center text-red-600 text-4xl mb-6 shadow-xl shadow-red-500/10 transition-transform hover:rotate-12">
                        ⚠️
                    </div>
                    <h1 className="text-3xl font-black text-gray-900 mb-4 tracking-tight">System Interruption</h1>
                    <p className="text-gray-500 max-w-md mb-8 leading-relaxed font-medium">
                        A critical error occurred in the KrishiSaarthi ecosystem. Our automated recovery systems are analyzing the trace.
                    </p>
                    <div className="flex flex-col sm:flex-row gap-4">
                        <button
                            onClick={() => window.location.reload()}
                            className="px-8 py-3 bg-gray-900 text-white rounded-2xl font-bold text-sm uppercase tracking-widest hover:bg-gray-800 transition-all active:scale-95 shadow-lg shadow-gray-900/10"
                        >
                            Retry Operation
                        </button>
                        <button
                            onClick={() => window.location.href = '/'}
                            className="px-8 py-3 bg-white text-gray-900 border border-gray-200 rounded-2xl font-bold text-sm uppercase tracking-widest hover:bg-gray-50 transition-all active:scale-95 shadow-sm"
                        >
                            Back to Safety
                        </button>
                    </div>
                    {import.meta.env.DEV && (
                        <div className="mt-12 p-6 bg-gray-100 rounded-2xl text-left font-mono text-xs text-gray-600 max-w-2xl overflow-auto border border-gray-200 shadow-inner">
                            <p className="font-bold text-red-600 mb-2 uppercase tracking-widest text-[9px]">Log Trace:</p>
                            {this.state.error?.toString()}
                        </div>
                    )}
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
