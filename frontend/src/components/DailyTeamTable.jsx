import React from 'react';
import { User, AlertCircle } from 'lucide-react';

const DailyTeamTable = ({ data }) => {
    if (!data || data.length === 0) return null;

    return (
        <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden h-full">
            <div className="p-6 border-b border-slate-100 flex justify-between items-center">
                <h3 className="text-lg font-bold text-slate-800">Performance da Equipe (Hoje)</h3>
                <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2 py-1 rounded-full">
                    {data.length} Membros
                </span>
            </div>
            <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                    <thead className="text-xs text-slate-500 uppercase bg-slate-50">
                        <tr>
                            <th className="px-6 py-3">Desenvolvedor</th>
                            <th className="px-6 py-3">Entregues (Hoje)</th>
                            <th className="px-6 py-3">Criados (Hoje)</th>
                            <th className="px-6 py-3">Status Recente</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        {data.map((member, i) => {
                            const isInactive = member.delivered_count === 0 && !member.recent_status;
                            const rowClass = isInactive ? 'bg-amber-50' : 'hover:bg-slate-50';
                            
                            return (
                                <tr key={i} className={rowClass}>
                                    <td className="px-6 py-4 font-medium text-slate-900 flex items-center gap-3">
                                        <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 shrink-0">
                                            <User className="w-4 h-4" />
                                        </div>
                                        <div className="flex items-center gap-2">
                                            {member.name}
                                            {isInactive && (
                                                <span className="text-amber-600" title="Sem atividade registrada hoje">
                                                    <AlertCircle className="w-4 h-4" />
                                                </span>
                                            )}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex flex-col">
                                            <span className="font-bold text-slate-800">{member.delivered_count} Tickets</span>
                                            <span className="text-xs text-slate-500">{member.delivered_sp} SP</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-slate-600">
                                        {member.created_count}
                                    </td>
                                    <td className="px-6 py-4">
                                        {member.recent_status ? (
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 whitespace-nowrap">
                                                {member.recent_status}
                                            </span>
                                        ) : (
                                            <span className="text-slate-400 italic text-xs">Sem atividade</span>
                                        )}
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default DailyTeamTable;
