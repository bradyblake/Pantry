/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {
			colors: {
				primary: {
					50: '#f0fdf4',
					100: '#dcfce7',
					200: '#bbf7d0',
					300: '#86efac',
					400: '#4ade80',
					500: '#22c55e',
					600: '#16a34a',
					700: '#15803d',
					800: '#166534',
					900: '#14532d'
				},
				accent: {
					50: '#fef3c7',
					100: '#fde68a',
					200: '#fcd34d',
					300: '#fbbf24',
					400: '#f59e0b',
					500: '#d97706',
					600: '#b45309'
				}
			},
			fontSize: {
				'touch': '1.125rem'
			},
			spacing: {
				'touch': '3rem',
				'touch-lg': '4rem'
			},
			boxShadow: {
				'card': '0 1px 3px 0 rgb(0 0 0 / 0.05), 0 1px 2px -1px rgb(0 0 0 / 0.05)',
				'card-hover': '0 4px 6px -1px rgb(0 0 0 / 0.07), 0 2px 4px -2px rgb(0 0 0 / 0.05)',
				'glow': '0 0 20px -5px rgb(34 197 94 / 0.4)',
				'glow-orange': '0 0 20px -5px rgb(249 115 22 / 0.4)',
				'glow-blue': '0 0 20px -5px rgb(59 130 246 / 0.4)'
			},
			animation: {
				'fade-in': 'fadeIn 0.2s ease-out',
				'slide-up': 'slideUp 0.3s ease-out',
				'pulse-soft': 'pulseSoft 2s ease-in-out infinite'
			},
			keyframes: {
				fadeIn: {
					'0%': { opacity: '0' },
					'100%': { opacity: '1' }
				},
				slideUp: {
					'0%': { opacity: '0', transform: 'translateY(10px)' },
					'100%': { opacity: '1', transform: 'translateY(0)' }
				},
				pulseSoft: {
					'0%, 100%': { opacity: '1' },
					'50%': { opacity: '0.7' }
				}
			}
		}
	},
	plugins: []
};
