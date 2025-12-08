import React from 'react';
import { Filter, LayoutDashboard, Settings } from 'lucide-react';

const Sidebar = ({ availableFilters, selectedFilters, onFilterChange }) => {
  
  const handleMultiSelectChange = (e, key) => {
    const options = e.target.options;
    const values = [];
    for (let i = 0, l = options.length; i < l; i++) {
      if (options[i].selected) {
        values.push(options[i].value);
      }
    }
    onFilterChange(key, values);
  };

  const handleProjectChange = (e) => {
    const options = e.target.options;
    const newValues = [];
    let todosSelected = false;

    for (let i = 0, l = options.length; i < l; i++) {
      if (options[i].selected) {
        newValues.push(options[i].value);
        if (options[i].value === 'Todos') todosSelected = true;
      }
    }
    
    // Logic for mutual exclusivity
    const wasTodosSelected = selectedFilters.projects.includes('Todos');
    let finalValues = newValues;

    if (todosSelected) {
        if (!wasTodosSelected) {
            // User just clicked Todos -> Clear others
            finalValues = ['Todos'];
        } else if (newValues.length > 1) {
             // User clicked something else while Todos was active -> Remove Todos
             finalValues = newValues.filter(v => v !== 'Todos');
        }
    } 
    
    onFilterChange('projects', finalValues);
  };

  return (
    <aside className="w-72 bg-white border-r border-slate-200 flex flex-col h-full shadow-sm z-10">
      <div className="p-6 border-b border-slate-100 flex items-center gap-3">
        <div className="w-8 h-8 bg-blue-700 rounded-lg flex items-center justify-center text-white font-bold shadow-sm p-1.5">
            <svg viewBox="0 0 24 24" fill="currentColor" className="w-full h-full">
              <path d="M11.53 2c0-1.1-.9-2-2-2H2C.9 0 0 .9 0 2v8c0 1.1.9 2 2 2h7.53c1.1 0 2-.9 2-2V2zm12.47 10c0-1.1-.9-2-2-2h-7.53c-1.1 0-2 .9-2 2v8c0 1.1.9 2 2 2H22c1.1 0 2-.9 2-2v-8zm-12.47 0c0-1.1-.9-2-2-2H2c-1.1 0-2 .9-2 2v8c0 1.1.9 2 2 2h7.53c1.1 0 2-.9 2-2v8c0 1.1.9 2 2 2h7.53c1.1 0 2-.9 2-2v-8z" className="hidden" /> {/* Legacy Block Logo */}
              <path d="M14.65 0l-5.6 5.6c-.78.78-.78 2.05 0 2.83l5.6 5.6c.78.78 2.05.78 2.83 0l5.6-5.6c.78-.78.78-2.05 0-2.83l-5.6-5.6c-.78-.79-2.05-.79-2.83 0zm-8.24 6.41L.81 12.01c-.78.78-.78 2.05 0 2.83l5.6 5.6c.78.78 2.05.78 2.83 0l5.6-5.6c.78-.78.78-2.05 0-2.83l-5.6-5.6c-.78-.79-2.04-.79-2.83 0z" />
            </svg>
        </div>
        <span className="font-bold text-lg text-slate-800 tracking-tight">Jira Analytics</span>
      </div>

      <div className="p-6 flex-1 overflow-y-auto">
        <div className="flex items-center gap-2 mb-6 text-slate-400 uppercase text-xs font-bold tracking-wider">
          <Filter size={14} />
          Filtros Globais
        </div>

        {/* Project Filter */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-700 mb-2">Projetos</label>
          <select 
            multiple 
            className="w-full p-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none min-h-[120px] bg-slate-50 text-slate-600"
            value={selectedFilters.projects}
            onChange={handleProjectChange}
          >
            <option value="Todos">Todos</option>
            {availableFilters.projects.map(p => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
          <p className="text-xs text-slate-400 mt-1">Segure Ctrl para selecionar múltiplos</p>
        </div>

        {/* Status Filter */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-700 mb-2">Status</label>
          <select 
            multiple 
            className="w-full p-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none min-h-[120px] bg-slate-50 text-slate-600"
            value={selectedFilters.statuses}
            onChange={(e) => handleMultiSelectChange(e, 'statuses')}
          >
            {availableFilters.statuses.map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>

        {/* Type Filter */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-700 mb-2">Tipo</label>
          <div className="space-y-2">
            {availableFilters.types.map(t => (
              <label key={t} className="flex items-center gap-2 text-sm text-slate-600 cursor-pointer hover:text-slate-900">
                <input 
                  type="checkbox" 
                  className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                  checked={selectedFilters.types.includes(t)}
                  onChange={(e) => {
                    const newTypes = e.target.checked 
                      ? [...selectedFilters.types, t]
                      : selectedFilters.types.filter(type => type !== t);
                    onFilterChange('types', newTypes);
                  }}
                />
                {t}
              </label>
            ))}
          </div>
        </div>
      </div>

      <div className="p-4 border-t border-slate-100 bg-slate-50">
        <button className="flex items-center gap-2 text-sm text-slate-500 hover:text-slate-800 transition-colors w-full p-2 rounded-lg hover:bg-white">
            <LayoutDashboard size={16} />
            Resetar Visão
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
