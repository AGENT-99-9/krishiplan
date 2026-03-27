import { Link } from 'react-router-dom';

export default function Footer() {
    const currentYear = new Date().getFullYear();

    const footerLinks = {
        Platform: [
            { label: 'AI Assistant', to: '/assistant' },
            { label: 'Marketplace', to: '/marketplace' },
            { label: 'Community', to: '/community' },
        ],
        Company: [
            { label: 'About Us', to: '#' },
            { label: 'Contact', to: '#' },
            { label: 'Careers', to: '#' },
        ],
        Legal: [
            { label: 'Privacy Policy', to: '#' },
            { label: 'Terms of Service', to: '#' },
            { label: 'Cookie Policy', to: '#' },
        ],
    };

    return (
        <footer className="bg-gray-900 text-gray-300">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-10">
                    {/* Brand */}
                    <div className="md:col-span-1">
                        <Link to="/" className="flex items-center gap-2 mb-4">
                            <div className="w-9 h-9 bg-gradient-to-br from-krishi-500 to-krishi-700 rounded-xl flex items-center justify-center">
                                <svg className="w-5 h-5 text-white" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M17.12 2.12c-2.34 0-4.69.96-6.36 2.64C8.41 7.12 7.56 10.22 8.12 13.12c-2.9-.56-6-.29-8.36 2.07a1 1 0 0 0 1.06 1.66c.1-.03 2.4-.82 4.18-.82.58 0 1.12.08 1.6.24a7.46 7.46 0 0 0 2.22 4.38 1 1 0 0 0 1.42-1.42 5.46 5.46 0 0 1-1.42-2.5c1.28.82 2.78 1.27 4.3 1.27 2.34 0 4.69-.96 6.36-2.64C23.58 11.26 23.58 5.42 19.76 2.12a1 1 0 0 0-.64-.24c-.7 0-1.38.08-2 .24z" />
                                </svg>
                            </div>
                            <span className="text-xl font-bold text-white">KrishiSaarthi</span>
                        </Link>
                        <p className="text-sm text-gray-400 leading-relaxed">
                            Empowering agriculture with intelligent insights, a robust marketplace, and a thriving community.
                        </p>
                    </div>

                    {/* Links */}
                    {Object.entries(footerLinks).map(([title, links]) => (
                        <div key={title}>
                            <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">
                                {title}
                            </h3>
                            <ul className="space-y-3">
                                {links.map((link) => (
                                    <li key={link.label}>
                                        <Link
                                            to={link.to}
                                            className="text-sm text-gray-400 hover:text-krishi-400 transition-colors duration-200"
                                        >
                                            {link.label}
                                        </Link>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>

                {/* Divider & copyright */}
                <div className="mt-12 pt-8 border-t border-gray-800 flex flex-col sm:flex-row items-center justify-between gap-4">
                    <p className="text-sm text-gray-500">
                        © {currentYear} KrishiSaarthi. All rights reserved.
                    </p>
                    <div className="flex items-center gap-4">
                        {/* Social Icons (placeholders) */}
                        {['Twitter', 'GitHub', 'LinkedIn'].map((social) => (
                            <a
                                key={social}
                                href="#"
                                className="text-gray-500 hover:text-krishi-400 transition-colors duration-200 text-sm"
                            >
                                {social}
                            </a>
                        ))}
                    </div>
                </div>
            </div>
        </footer>
    );
}
