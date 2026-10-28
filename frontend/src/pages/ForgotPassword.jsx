import { useState } from 'react';
import { Link } from 'react-router-dom';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!email) return;
    
    setLoading(true);
    try {
      await fetch('/api/auth/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });
      // Always show success to prevent email enumeration
      setSubmitted(true);
    } catch (error) {
      console.error(error);
      setSubmitted(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F7F3EA] flex flex-col justify-center py-12 sm:px-6 lg:px-8 font-sans">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-editorial font-bold text-[#1F3A32]">
          Reset Password
        </h2>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow-sm border border-[#E6EEEC] sm:rounded-lg sm:px-10">
          {submitted ? (
            <div className="text-center">
              <div className="rounded-full bg-green-100 p-3 mx-auto w-12 h-12 flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                </svg>
              </div>
              <h3 className="text-lg font-medium text-[#1F3A32] mb-2">Check your email</h3>
              <p className="text-sm text-[#4A4A43] mb-6">
                If an account exists for {email}, we have sent password reset instructions.
              </p>
              <Link to="/login" className="font-medium text-[#D97745] hover:text-[#C56331] text-sm">
                Return to Login
              </Link>
            </div>
          ) : (
            <form className="space-y-6" onSubmit={handleSubmit}>
              <p className="text-sm text-[#4A4A43] text-center">
                Enter your email address and we'll send you a link to reset your password.
              </p>
              
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-[#4A4A43]">
                  Email address
                </label>
                <div className="mt-1">
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="appearance-none block w-full px-3 py-2 border border-[#CBD5E1] rounded-md shadow-sm placeholder-[#94A3B8] focus:outline-none focus:ring-[#294D42] focus:border-[#294D42] sm:text-sm"
                  />
                </div>
              </div>

              <div>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-[#F7F3EA] bg-[#1F3A32] hover:bg-[#162C26] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#294D42] disabled:opacity-70 transition-colors"
                >
                  {loading ? 'Sending...' : 'Send Reset Link'}
                </button>
              </div>
              
              <div className="mt-6 text-center">
                <Link to="/login" className="font-medium text-[#D97745] hover:text-[#C56331] text-sm">
                  Back to Login
                </Link>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
