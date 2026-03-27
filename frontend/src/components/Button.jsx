import { Link } from 'react-router-dom';

export default function Button({
    children,
    to,
    variant = 'primary',
    className = '',
    onClick,
    type = 'button',
    ...props
}) {
    const base =
        'inline-flex items-center justify-center font-semibold transition-all duration-300 rounded-full cursor-pointer focus:outline-none focus:ring-2 focus:ring-offset-2';

    const variants = {
        primary:
            'bg-krishi-600 text-white px-8 py-3.5 text-base hover:bg-krishi-700 hover:shadow-lg hover:shadow-krishi-500/25 focus:ring-krishi-500 active:scale-[0.97]',
        secondary:
            'bg-white text-krishi-700 border-2 border-krishi-600 px-8 py-3.5 text-base hover:bg-krishi-50 hover:shadow-lg focus:ring-krishi-500 active:scale-[0.97]',
        ghost:
            'text-gray-700 px-5 py-2.5 text-sm hover:text-krishi-600 hover:bg-krishi-50 focus:ring-krishi-500',
        nav:
            'text-gray-600 px-4 py-2 text-sm font-medium hover:text-krishi-600 transition-colors duration-200',
    };

    const classes = `${base} ${variants[variant] || variants.primary} ${className}`;

    if (to) {
        return (
            <Link to={to} className={classes} {...props}>
                {children}
            </Link>
        );
    }

    return (
        <button type={type} className={classes} onClick={onClick} {...props}>
            {children}
        </button>
    );
}
