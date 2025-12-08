import React from 'react';
import KpiCard from './KpiCard';
import BurndownChart from './charts/BurndownChart';
import StatusChart from './charts/StatusChart';
import TypeDistributionChart from './charts/TypeDistributionChart';
import { LayoutList, CheckCircle2, AlertOctagon, Bug } from 'lucide-react';

const Dashboard = ({ data }) => {
    if (!data) return null;

    const { kpis, charts } = data;

    return (
        <div className="space-y-6">
            {/* KPIs */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <KpiCard 
                    title="Total Issues" 
                    value={kpis.total} 
                    icon={LayoutList}
                    subtext="Backlog Total"
                />
                <KpiCard 
                    title="Ativas" 
                    value={kpis.active} 
                    type="primary"
                    icon={AlertOctagon}
                    subtext="Em andamento"
                />
                <KpiCard 
                    title="Entregues" 
                    value={kpis.done} 
                    type="success"
                    icon={CheckCircle2}
                    subtext="Concluídas"
                />
                <KpiCard 
                    title="Bugs" 
                    value={kpis.bugs} 
                    type="danger"
                    icon={Bug}
                    subtext="Reportados"
                />
            </div>

            {/* Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Burndown */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <h3 className="text-lg font-bold text-slate-800 mb-4">Evolução do Escopo (Burnup)</h3>
                    <BurndownChart data={charts.burndown} />
                </div>

                {/* Status by Project */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <h3 className="text-lg font-bold text-slate-800 mb-4">Status por Projeto</h3>
                    <StatusChart data={charts.status_by_project} />
                </div>

                {/* Type Distribution */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <h3 className="text-lg font-bold text-slate-800 mb-4">Distribuição por Tipo</h3>
                    <TypeDistributionChart data={charts.type_distribution} />
                </div>

                 {/* Team Load */}
                 <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <h3 className="text-lg font-bold text-slate-800 mb-4">Carga da Equipe</h3>
                    <div className="overflow-auto max-h-[300px]">
                        <table className="w-full text-sm text-left">
                            <thead className="text-xs text-slate-500 uppercase bg-slate-50">
                                <tr>
                                    <th className="px-4 py-2">Responsável</th>
                                    <th className="px-4 py-2">Issues</th>
                                    <th className="px-4 py-2">Pontos</th>
                                </tr>
                            </thead>
                            <tbody>
                                {charts.team_load && charts.team_load.map((member, i) => (
                                    <tr key={i} className="border-b border-slate-50 hover:bg-slate-50">
                                        <td className="px-4 py-3 font-medium text-slate-900">{member.Responsável}</td>
                                        <td className="px-4 py-3 text-slate-600">{member.issues}</td>
                                        <td className="px-4 py-3 text-blue-600 font-bold">{member.points}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;