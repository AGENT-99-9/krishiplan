import { z } from 'zod';

export const loginSchema = z.object({
    email: z
        .string()
        .min(1, 'Email is required')
        .email('Please enter a valid email address'),
    password: z
        .string()
        .min(6, 'Password must be at least 6 characters'),
});

export const signupSchema = z.object({
    full_name: z
        .string()
        .min(1, 'Full name is required')
        .max(100, 'Full name is too long'),
    email: z
        .string()
        .min(1, 'Email is required')
        .email('Please enter a valid email address'),
    password: z
        .string()
        .min(6, 'Password must be at least 6 characters'),
    role: z.enum(['farmer', 'vendor', 'admin']).default('farmer'),
    shop_name: z.string().optional(),
    location: z.string().optional(),
}).superRefine((data, ctx) => {
    if (data.role === 'vendor') {
        if (!data.shop_name || data.shop_name.trim() === '') {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                message: 'Shop name is required for vendors',
                path: ['shop_name'],
            });
        }
        if (!data.location || data.location.trim() === '') {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                message: 'Location is required for vendors',
                path: ['location'],
            });
        }
    }
});
