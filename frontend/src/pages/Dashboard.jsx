import { ArrowUpRight, ArrowDownLeft, Wallet, CreditCard, DollarSign } from 'lucide-react';

const Dashboard = () => {
    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-secondary-900">Dashboard</h1>
                    <p className="text-secondary-500">Welcome back, Alex. Here's what's happening with your accounts.</p>
                </div>
                <div className="flex gap-3">
                    <button className="px-4 py-2 bg-white border border-secondary-200 text-secondary-700 rounded-lg font-medium hover:bg-secondary-50 transition-colors">
                        Download Report
                    </button>
                    <button className="px-4 py-2 bg-brand-600 text-white rounded-lg font-medium hover:bg-brand-700 transition-colors shadow-sm">
                        Add Money
                    </button>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white p-6 rounded-xl border border-secondary-200 shadow-sm">
                    <div className="flex items-center justify-between mb-4">
                        <div className="p-2 bg-brand-50 text-brand-600 rounded-lg">
                            <Wallet size={24} />
                        </div>
                        <span className="text-sm font-medium text-green-600 flex items-center gap-1">
                            <ArrowUpRight size={16} /> +2.5%
                        </span>
                    </div>
                    <p className="text-secondary-500 text-sm font-medium">Total Balance</p>
                    <h3 className="text-2xl font-bold text-secondary-900 mt-1">$124,500.00</h3>
                </div>

                <div className="bg-white p-6 rounded-xl border border-secondary-200 shadow-sm">
                    <div className="flex items-center justify-between mb-4">
                        <div className="p-2 bg-green-50 text-green-600 rounded-lg">
                            <ArrowDownLeft size={24} />
                        </div>
                        <span className="text-sm font-medium text-green-600 flex items-center gap-1">
                            <ArrowUpRight size={16} /> +4.2%
                        </span>
                    </div>
                    <p className="text-secondary-500 text-sm font-medium">Total Income</p>
                    <h3 className="text-2xl font-bold text-secondary-900 mt-1">$8,250.00</h3>
                </div>

                <div className="bg-white p-6 rounded-xl border border-secondary-200 shadow-sm">
                    <div className="flex items-center justify-between mb-4">
                        <div className="p-2 bg-red-50 text-red-600 rounded-lg">
                            <ArrowUpRight size={24} />
                        </div>
                        <span className="text-sm font-medium text-red-600 flex items-center gap-1">
                            <ArrowUpRight size={16} /> +1.2%
                        </span>
                    </div>
                    <p className="text-secondary-500 text-sm font-medium">Total Expenses</p>
                    <h3 className="text-2xl font-bold text-secondary-900 mt-1">$3,400.00</h3>
                </div>
            </div>

            {/* Recent Activity Section Placeholder */}
            <div className="bg-white rounded-xl border border-secondary-200 shadow-sm">
                <div className="p-6 border-b border-secondary-200 flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-secondary-900">Recent Activity</h3>
                    <button className="text-brand-600 text-sm font-medium hover:text-brand-700">View All</button>
                </div>
                <div className="p-6">
                    <p className="text-secondary-500 text-center py-8">No recent transactions to display.</p>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
