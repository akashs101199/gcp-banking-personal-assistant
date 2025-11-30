import { Outlet } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import VoiceChat from '../components/VoiceChat';

const MainLayout = () => {
    return (
        <div className="flex min-h-screen bg-secondary-50">
            <Sidebar />
            <div className="flex-1 ml-64 flex flex-col">
                <Header />
                <main className="flex-1 p-8 overflow-y-auto relative">
                    <Outlet />
                    <VoiceChat />
                </main>
            </div>
        </div>
    );
};

export default MainLayout;
