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
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const data = await getDashboardData(selectedFilters);
        setDashboardData(data);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [selectedFilters]);

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
      />

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto p-8">
        <header className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-slate-800 tracking-tight">Executive Dashboard</h1>
            <p className="text-slate-500 mt-1">Visão estratégica e operacional do portfólio</p>
          </div>
          <div className="text-sm text-slate-400">
            Atualizado em: {new Date().toLocaleTimeString()}
          </div>
        </header>

        {loading ? (
          <div className="flex h-64 items-center justify-center">
            <Loader2 className="h-10 w-10 animate-spin text-blue-600" />
            <span className="ml-3 text-slate-500 font-medium">Carregando dados...</span>
          </div>
        ) : (
          <Dashboard data={dashboardData} />
        )}
      </main>
    </div>
  );
}

export default App;