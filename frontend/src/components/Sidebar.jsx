import { Home, CreditCard, ArrowRightLeft, Banknote, Settings, LogOut, RefreshCw } from 'lucide-react';
import { NavLink } from 'react-router-dom';
import clsx from 'clsx';

const Sidebar = () => {
    const navItems = [
        { icon: Home, label: 'Dashboard', path: '/' },
        { icon: Banknote, label: 'Accounts', path: '/accounts' },
        { icon: ArrowRightLeft, label: 'Transfers', path: '/transfers' },
        { icon: RefreshCw, label: 'Exchange', path: '/exchange' },
        { icon: CreditCard, label: 'Cards', path: '/cards' },
        { icon: Settings, label: 'Settings', path: '/settings' },
    ];

    return (
        <aside className="w-64 bg-brand-900 text-white h-screen fixed left-0 top-0 flex flex-col border-r border-brand-800">
            <div className="p-6 border-b border-brand-800">
                <h1 className="text-2xl font-bold tracking-tight">Intl Bank</h1>
            </div>

            <nav className="flex-1 p-4 space-y-2">
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) =>
                            clsx(
                                'flex items-center gap-3 px-4 py-3 rounded-lg transition-colors',
                                isActive
                                    ? 'bg-brand-700 text-white shadow-sm'
                                    : 'text-brand-200 hover:bg-brand-800 hover:text-white'
                            )
                        }
                    >
                        <item.icon size={20} />
                        <span className="font-medium">{item.label}</span>
                    </NavLink>
                ))}
            </nav>

            <div className="p-4 border-t border-brand-800">
                <button className="flex items-center gap-3 px-4 py-3 w-full text-brand-200 hover:bg-brand-800 hover:text-white rounded-lg transition-colors">
                    <LogOut size={20} />
                    <span className="font-medium">Sign Out</span>
                </button>
            </div>
        </aside>
    );
};

export default Sidebar;
