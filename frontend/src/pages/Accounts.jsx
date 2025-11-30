import { ArrowDownLeft, ArrowUpRight, Search, Filter } from 'lucide-react';

const Accounts = () => {
    const accounts = [
        { id: 1, name: 'Main Checking', number: '**** 4521', balance: 24500.00, currency: 'USD', type: 'Checking' },
        { id: 2, name: 'Savings Plus', number: '**** 8892', balance: 85000.00, currency: 'USD', type: 'Savings' },
        { id: 3, name: 'Euro Travel', number: '**** 1234', balance: 4250.00, currency: 'EUR', type: 'Checking' },
    ];

    const transactions = [
        { id: 1, description: 'Apple Store', date: 'Today, 2:30 PM', amount: -129.00, type: 'debit', category: 'Shopping' },
        { id: 2, description: 'Salary Deposit', date: 'Yesterday, 9:00 AM', amount: 4500.00, type: 'credit', category: 'Income' },
        { id: 3, description: 'Uber', date: 'Yesterday, 6:15 PM', amount: -24.50, type: 'debit', category: 'Transport' },
        { id: 4, description: 'Starbucks', date: 'Nov 28, 8:45 AM', amount: -5.40, type: 'debit', category: 'Food' },
        { id: 5, description: 'Transfer from Savings', date: 'Nov 27, 10:00 AM', amount: 1000.00, type: 'credit', category: 'Transfer' },
    ];

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-secondary-900">Accounts</h1>
                <button className="px-4 py-2 bg-brand-600 text-white rounded-lg font-medium hover:bg-brand-700 transition-colors shadow-sm">
                    Open New Account
                </button>
            </div>

            {/* Accounts Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {accounts.map((account) => (
                    <div key={account.id} className="bg-white p-6 rounded-xl border border-secondary-200 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
                        <div className="flex justify-between items-start mb-4">
                            <div>
                                <p className="text-secondary-500 text-sm font-medium">{account.type}</p>
                                <h3 className="text-lg font-bold text-secondary-900">{account.name}</h3>
                            </div>
                            <span className="bg-brand-50 text-brand-700 text-xs font-bold px-2 py-1 rounded">{account.currency}</span>
                        </div>
                        <div className="mt-4">
                            <p className="text-2xl font-bold text-secondary-900">
                                {account.currency === 'USD' ? '$' : '€'}{account.balance.toLocaleString()}
                            </p>
                            <p className="text-secondary-400 text-sm mt-1">{account.number}</p>
                        </div>
                    </div>
                ))}
            </div>

            {/* Transactions Section */}
            <div className="bg-white rounded-xl border border-secondary-200 shadow-sm">
                <div className="p-6 border-b border-secondary-200 flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-secondary-900">Transaction History</h3>
                    <div className="flex gap-3">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary-400" size={16} />
                            <input
                                type="text"
                                placeholder="Search..."
                                className="pl-9 pr-4 py-2 bg-secondary-50 border border-secondary-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                            />
                        </div>
                        <button className="flex items-center gap-2 px-3 py-2 border border-secondary-200 rounded-lg text-sm font-medium text-secondary-700 hover:bg-secondary-50">
                            <Filter size={16} /> Filter
                        </button>
                    </div>
                </div>
                <div className="divide-y divide-secondary-100">
                    {transactions.map((tx) => (
                        <div key={tx.id} className="p-4 flex items-center justify-between hover:bg-secondary-50 transition-colors">
                            <div className="flex items-center gap-4">
                                <div className={`p-2 rounded-full ${tx.type === 'credit' ? 'bg-green-100 text-green-600' : 'bg-secondary-100 text-secondary-600'}`}>
                                    {tx.type === 'credit' ? <ArrowDownLeft size={20} /> : <ArrowUpRight size={20} />}
                                </div>
                                <div>
                                    <p className="font-medium text-secondary-900">{tx.description}</p>
                                    <p className="text-sm text-secondary-500">{tx.date} • {tx.category}</p>
                                </div>
                            </div>
                            <span className={`font-semibold ${tx.type === 'credit' ? 'text-green-600' : 'text-secondary-900'}`}>
                                {tx.type === 'credit' ? '+' : ''}{tx.amount.toLocaleString('en-US', { style: 'currency', currency: 'USD' })}
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Accounts;
