import React, { useState, useEffect } from 'react';
import { getFilters, getDashboardData } from './lib/api';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import { Loader2 } from 'lucide-react';

function App() {
  const [loading, setLoading] = useState(true);
  const [availableFilters, setAvailableFilters] = useState({
    projects: [],
    statuses: [],
    types: [],
    assignees: []
  });
  
  const [selectedFilters, setSelectedFilters] = useState({
    projects: [],
    statuses: [],
    types: [],
    period: "Tudo"
  });

  const [dashboardData, setDashboardData] = useState(null);

  // Load initial filters
  useEffect(() => {
    const fetchFilters = async () => {
      try {
        const data = await getFilters();
        setAvailableFilters(data);
      } catch (error) {
        console.error("Error fetching filters:", error);
      }
    };
    fetchFilters();
  }, []);

  // Load dashboard data when filters change
  const fetchData = async (forceRefresh = false) => {
    setLoading(true);
    try {
      const data = await getDashboardData({ ...selectedFilters, force_refresh: forceRefresh });
      setDashboardData(data);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedFilters]);

  const handleRefresh = () => {
    fetchData(true);
  };

  const handleFilterChange = (key, value) => {
    setSelectedFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden font-sans text-slate-900">
      {/* Sidebar */}
      <Sidebar 
        availableFilters={availableFilters}
        selectedFilters={selectedFilters}
        onFilterChange={handleFilterChange}
        onRefresh={handleRefresh}
      />

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto p-8">
        <header className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-slate-800 tracking-tight">FFID Dashboard</h1>
            <p className="text-slate-500 mt-1">Visão estratégica e operacional do portfólio</p>
          </div>
          <div className="text-sm text-slate-400">
            Atualizado em: {new Date().toLocaleTimeString()}
          </div>
        </header>

        <div className="relative min-h-[400px]">
          {loading && (
            <div className={`absolute inset-0 bg-white/80 z-20 flex items-center justify-center backdrop-blur-sm rounded-xl transition-all duration-300 ${!dashboardData ? 'h-64 static bg-transparent' : ''}`}>
               <div className="flex flex-col items-center gap-3">
                  <Loader2 className="h-10 w-10 animate-spin text-blue-600" />
                  <span className="text-slate-500 font-medium">Carregando dados...</span>
               </div>
            </div>
          )}
          
          {dashboardData && (
             <div className={loading ? 'opacity-50 pointer-events-none filter blur-[1px] transition-all duration-300' : 'transition-all duration-300'}>
                <Dashboard data={dashboardData} />
             </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;