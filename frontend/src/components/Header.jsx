import { Bell, Search, User } from 'lucide-react';

const Header = () => {
    return (
        <header className="h-16 bg-white border-b border-secondary-200 flex items-center justify-between px-8 sticky top-0 z-10">
            <div className="flex items-center gap-4 w-96">
                <div className="relative w-full">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary-400" size={18} />
                    <input
                        type="text"
                        placeholder="Search transactions, accounts..."
                        className="w-full pl-10 pr-4 py-2 bg-secondary-50 border border-secondary-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent text-sm"
                    />
                </div>
            </div>

            <div className="flex items-center gap-6">
                <button className="relative text-secondary-500 hover:text-brand-600 transition-colors">
                    <Bell size={20} />
                    <span className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full"></span>
                </button>

                <div className="flex items-center gap-3 pl-6 border-l border-secondary-200">
                    <div className="text-right hidden md:block">
                        <p className="text-sm font-semibold text-secondary-900">Alex Morgan</p>
                        <p className="text-xs text-secondary-500">Premium Member</p>
                    </div>
                    <div className="w-10 h-10 bg-brand-100 rounded-full flex items-center justify-center text-brand-700 border border-brand-200">
                        <User size={20} />
                    </div>
                </div>
            </div>
        </header>
    );
};

export default Header;
