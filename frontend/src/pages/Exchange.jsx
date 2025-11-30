import { useState } from 'react';
import { ArrowRightLeft, TrendingUp, RefreshCw } from 'lucide-react';

const Exchange = () => {
    const [fromCurrency, setFromCurrency] = useState('USD');
    const [toCurrency, setToCurrency] = useState('EUR');
    const [amount, setAmount] = useState('');

    const rates = {
        'USD': { 'EUR': 0.92, 'GBP': 0.79, 'JPY': 148.50 },
        'EUR': { 'USD': 1.09, 'GBP': 0.86, 'JPY': 161.20 },
        'GBP': { 'USD': 1.27, 'EUR': 1.16, 'JPY': 188.40 },
    };

    const convert = () => {
        if (!amount) return '0.00';
        const rate = rates[fromCurrency]?.[toCurrency] || 1;
        return (parseFloat(amount) * rate).toFixed(2);
    };

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            <h1 className="text-2xl font-bold text-secondary-900">Currency Exchange</h1>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Exchange Form */}
                <div className="md:col-span-2 bg-white p-8 rounded-xl border border-secondary-200 shadow-sm">
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-lg font-semibold text-secondary-900">Convert Currency</h2>
                        <div className="flex items-center gap-2 text-sm text-secondary-500">
                            <RefreshCw size={14} /> Live rates
                        </div>
                    </div>

                    <div className="space-y-6">
                        <div className="p-4 bg-secondary-50 rounded-xl border border-secondary-200">
                            <div className="flex justify-between mb-2">
                                <label className="text-sm font-medium text-secondary-500">You Pay</label>
                                <span className="text-sm font-medium text-secondary-900">Balance: $24,500.00</span>
                            </div>
                            <div className="flex gap-4">
                                <select
                                    value={fromCurrency}
                                    onChange={(e) => setFromCurrency(e.target.value)}
                                    className="bg-transparent font-bold text-xl text-secondary-900 focus:outline-none cursor-pointer"
                                >
                                    <option value="USD">USD</option>
                                    <option value="EUR">EUR</option>
                                    <option value="GBP">GBP</option>
                                </select>
                                <input
                                    type="number"
                                    value={amount}
                                    onChange={(e) => setAmount(e.target.value)}
                                    placeholder="0.00"
                                    className="w-full bg-transparent text-right text-3xl font-bold text-secondary-900 focus:outline-none placeholder:text-secondary-300"
                                />
                            </div>
                        </div>

                        <div className="flex justify-center -my-3 relative z-10">
                            <button
                                onClick={() => {
                                    setFromCurrency(toCurrency);
                                    setToCurrency(fromCurrency);
                                }}
                                className="p-2 bg-white border border-secondary-200 rounded-full shadow-sm hover:bg-secondary-50 transition-colors text-brand-600"
                            >
                                <ArrowRightLeft size={20} />
                            </button>
                        </div>

                        <div className="p-4 bg-secondary-50 rounded-xl border border-secondary-200">
                            <div className="flex justify-between mb-2">
                                <label className="text-sm font-medium text-secondary-500">You Receive</label>
                                <span className="text-sm font-medium text-brand-600">
                                    1 {fromCurrency} = {rates[fromCurrency]?.[toCurrency]} {toCurrency}
                                </span>
                            </div>
                            <div className="flex gap-4">
                                <select
                                    value={toCurrency}
                                    onChange={(e) => setToCurrency(e.target.value)}
                                    className="bg-transparent font-bold text-xl text-secondary-900 focus:outline-none cursor-pointer"
                                >
                                    <option value="USD">USD</option>
                                    <option value="EUR">EUR</option>
                                    <option value="GBP">GBP</option>
                                </select>
                                <input
                                    type="text"
                                    readOnly
                                    value={convert()}
                                    className="w-full bg-transparent text-right text-3xl font-bold text-secondary-900 focus:outline-none"
                                />
                            </div>
                        </div>

                        <button className="w-full py-4 bg-brand-600 text-white rounded-xl font-bold text-lg hover:bg-brand-700 transition-colors shadow-lg shadow-brand-200">
                            Convert Now
                        </button>
                    </div>
                </div>

                {/* Market Rates */}
                <div className="space-y-6">
                    <div className="bg-brand-900 text-white p-6 rounded-xl shadow-lg">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="p-2 bg-brand-800 rounded-lg">
                                <TrendingUp size={20} />
                            </div>
                            <div>
                                <p className="font-medium">Market Analysis</p>
                                <p className="text-xs text-brand-300">Last 24 hours</p>
                            </div>
                        </div>
                        <div className="space-y-4">
                            <div className="flex justify-between items-center">
                                <span className="text-brand-200">EUR/USD</span>
                                <span className="font-bold text-green-400">+0.45%</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-brand-200">GBP/USD</span>
                                <span className="font-bold text-red-400">-0.12%</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-brand-200">USD/JPY</span>
                                <span className="font-bold text-green-400">+0.88%</span>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white p-6 rounded-xl border border-secondary-200 shadow-sm">
                        <h3 className="font-semibold text-secondary-900 mb-4">Popular Pairs</h3>
                        <div className="space-y-3">
                            {['USD/EUR', 'USD/GBP', 'EUR/GBP'].map((pair) => (
                                <div key={pair} className="flex items-center justify-between p-3 hover:bg-secondary-50 rounded-lg cursor-pointer transition-colors">
                                    <span className="font-medium text-secondary-700">{pair}</span>
                                    <ArrowRightLeft size={16} className="text-secondary-400" />
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Exchange;
