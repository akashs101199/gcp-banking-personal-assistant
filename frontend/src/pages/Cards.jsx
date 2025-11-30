import { CreditCard, Plus, Shield, Lock } from 'lucide-react';

const Cards = () => {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-secondary-900">My Cards</h1>
                <button className="flex items-center gap-2 px-4 py-2 bg-brand-600 text-white rounded-lg font-medium hover:bg-brand-700 transition-colors shadow-sm">
                    <Plus size={18} /> Add New Card
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Card Preview */}
                <div className="space-y-6">
                    <div className="relative h-56 w-96 bg-gradient-to-br from-brand-900 to-brand-700 rounded-2xl p-6 text-white shadow-xl mx-auto md:mx-0">
                        <div className="flex justify-between items-start">
                            <span className="text-lg font-bold tracking-wider">Intl Bank</span>
                            <CreditCard size={32} className="opacity-80" />
                        </div>
                        <div className="mt-10">
                            <span className="text-2xl tracking-widest font-mono">4521 8892 1234 9988</span>
                        </div>
                        <div className="mt-8 flex justify-between items-end">
                            <div>
                                <p className="text-xs text-brand-200 uppercase">Card Holder</p>
                                <p className="font-medium tracking-wide">ALEX MORGAN</p>
                            </div>
                            <div>
                                <p className="text-xs text-brand-200 uppercase">Expires</p>
                                <p className="font-medium tracking-wide">09/28</p>
                            </div>
                        </div>
                    </div>

                    <div className="flex justify-center gap-4">
                        <button className="flex flex-col items-center gap-2 p-4 bg-white border border-secondary-200 rounded-xl w-24 hover:bg-secondary-50 transition-colors">
                            <Lock size={20} className="text-secondary-600" />
                            <span className="text-xs font-medium text-secondary-700">Lock</span>
                        </button>
                        <button className="flex flex-col items-center gap-2 p-4 bg-white border border-secondary-200 rounded-xl w-24 hover:bg-secondary-50 transition-colors">
                            <Shield size={20} className="text-secondary-600" />
                            <span className="text-xs font-medium text-secondary-700">Limits</span>
                        </button>
                        <button className="flex flex-col items-center gap-2 p-4 bg-white border border-secondary-200 rounded-xl w-24 hover:bg-secondary-50 transition-colors">
                            <CreditCard size={20} className="text-secondary-600" />
                            <span className="text-xs font-medium text-secondary-700">Details</span>
                        </button>
                    </div>
                </div>

                {/* Card Settings */}
                <div className="bg-white rounded-xl border border-secondary-200 shadow-sm p-6">
                    <h3 className="text-lg font-semibold text-secondary-900 mb-4">Card Settings</h3>
                    <div className="space-y-4">
                        <div className="flex items-center justify-between p-3 hover:bg-secondary-50 rounded-lg transition-colors cursor-pointer">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-brand-50 text-brand-600 rounded-lg">
                                    <Globe size={20} />
                                </div>
                                <div>
                                    <p className="font-medium text-secondary-900">International Usage</p>
                                    <p className="text-xs text-secondary-500">Allow transactions outside home country</p>
                                </div>
                            </div>
                            <div className="w-11 h-6 bg-brand-600 rounded-full relative cursor-pointer">
                                <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full"></div>
                            </div>
                        </div>

                        <div className="flex items-center justify-between p-3 hover:bg-secondary-50 rounded-lg transition-colors cursor-pointer">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-brand-50 text-brand-600 rounded-lg">
                                    <CreditCard size={20} />
                                </div>
                                <div>
                                    <p className="font-medium text-secondary-900">Contactless Payments</p>
                                    <p className="text-xs text-secondary-500">Enable tap to pay</p>
                                </div>
                            </div>
                            <div className="w-11 h-6 bg-brand-600 rounded-full relative cursor-pointer">
                                <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

// Missing import fix
import { Globe } from 'lucide-react';

export default Cards;
