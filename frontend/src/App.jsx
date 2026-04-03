import { Routes, Route } from 'react-router-dom';
import { AppProvider } from './store/AppContext';
import Sidebar from './components/layout/Sidebar';
import Dashboard from './pages/Dashboard';
import Policy from './pages/Policy';
import Earnings from './pages/Earnings';
import Payouts from './pages/Payouts';
import Admin from './pages/Admin';
import RiskPool from './pages/RiskPool';
import Heatmap from './pages/Heatmap';

export default function App() {
  return (
    <AppProvider>
      <div className="flex h-screen overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/"          element={<Dashboard />} />
            <Route path="/policy"    element={<Policy />} />
            <Route path="/earnings"  element={<Earnings />} />
            <Route path="/payouts"   element={<Payouts />} />
            <Route path="/admin"     element={<Admin />} />
            <Route path="/risk-pool" element={<RiskPool />} />
            <Route path="/heatmap"   element={<Heatmap />} />
          </Routes>
        </main>
      </div>
    </AppProvider>
  );
}
