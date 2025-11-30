import { useState } from 'react';
import { ArrowRight, Globe, Building2, User } from 'lucide-react';
import clsx from 'clsx';

const Transfers = () => {
    const [activeTab, setActiveTab] = useState('domestic');

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            <h1 className="text-2xl font-bold text-secondary-900">Transfers</h1>

            {/* Tabs */}
            <div className="flex p-1 bg-secondary-100 rounded-xl w-fit">
                <button
                    onClick={() => setActiveTab('domestic')}
                    className={clsx(
                        'px-6 py-2 rounded-lg text-sm font-medium transition-all',
                        activeTab === 'domestic' ? 'bg-white text-brand-700 shadow-sm' : 'text-secondary-600 hover:text-secondary-900'
                    )}
                >
                    Domestic Transfer
                </button>
                <button
                    onClick={() => setActiveTab('international')}
                    className={clsx(
                        'px-6 py-2 rounded-lg text-sm font-medium transition-all',
                        activeTab === 'international' ? 'bg-white text-brand-700 shadow-sm' : 'text-secondary-600 hover:text-secondary-900'
                    )}
                >
                    International (SWIFT)
                </button>
            </div>

            <div className="bg-white p-8 rounded-xl border border-secondary-200 shadow-sm">
                <form className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-secondary-700">From Account</label>
                            <select className="w-full p-3 bg-secondary-50 border border-secondary-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500">
                                <option>Main Checking (**** 4521) - $24,500.00</option>
                                <option>Savings Plus (**** 8892) - $85,000.00</option>
                            </select>
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-secondary-700">Amount</label>
                            <div className="relative">
                                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary-500 font-medium">$</span>
                                <input
                                    type="number"
                                    placeholder="0.00"
                                    className="w-full pl-8 pr-4 p-3 bg-secondary-50 border border-secondary-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500"
                                />
                            </div>
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-secondary-700">Recipient</label>
                        <div className="relative">
                            <User className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary-400" size={18} />
                            <input
                                type="text"
                                placeholder="Name or Email"
                                className="w-full pl-10 pr-4 p-3 bg-secondary-50 border border-secondary-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500"
                            />
                        </div>
                    </div>

                    {activeTab === 'international' && (
                        <div className="space-y-4 pt-4 border-t border-secondary-100 animate-in fade-in slide-in-from-top-2">
                            <div className="flex items-center gap-2 text-brand-700 bg-brand-50 p-3 rounded-lg text-sm">
                                <Globe size={18} />
                                <span>International transfers may take 1-3 business days.</span>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-secondary-700">SWIFT / BIC Code</label>
                                    <div className="relative">
                                        <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary-400" size={18} />
                                        <input
                                            type="text"
                                            placeholder="ABCDUS33"
                                            className="w-full pl-10 pr-4 p-3 bg-secondary-50 border border-secondary-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 uppercase"
                                        />
                                    </div>
                                </div>
                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-secondary-700">IBAN / Account Number</label>
                                    <input
                                        type="text"
                                        placeholder="US12 3456 7890 1234"
                                        className="w-full p-3 bg-secondary-50 border border-secondary-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500"
                                    />
                                </div>
                            </div>
                        </div>
                    )}

                    <div className="pt-4">
                        <button type="button" className="w-full py-3 bg-brand-600 text-white rounded-lg font-bold hover:bg-brand-700 transition-colors shadow-sm flex items-center justify-center gap-2">
                            Review Transfer <ArrowRight size={18} />
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default Transfers;
