import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'ORION-Q | Institutional Market Terminal & Quantitative Intelligence Engine',
  description: 'Full-stack financial market terminal, calibrated prediction parliament, 95% conformal intervals, SHAP explainability, and real-time market session router.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" style={{ background: '#070a12', color: '#f8fafc' }}>
      <body style={{ background: '#070a12', color: '#f8fafc', margin: 0, padding: 0, minHeight: '100vh' }}>
        {children}
      </body>
    </html>
  );
}
