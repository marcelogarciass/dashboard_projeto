import React, { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LabelList } from 'recharts';

const StatusChart = ({ data }) => {
    const processedData = useMemo(() => {
        if (!data) return [];
        const pivoted = {};
        const statuses = new Set();
        const STATUS_DONE = ['Concluído', 'Done', 'Finalizado', 'Resolvido', 'Closed'];

        data.forEach(item => {
            if (STATUS_DONE.includes(item.Status)) return;

            if (!pivoted[item.Projeto]) {
                pivoted[item.Projeto] = { name: item.Projeto };
            }
            pivoted[item.Projeto][item.Status] = item.count;
            statuses.add(item.Status);
        });

        // Define specific order requested by user
        const STATUS_ORDER = [
            'Tarefas pendentes', 
            'Escalados', 
            'Escalated',
            'Em andamento', 
            'pronto para qa', 
            'aguardando aprovação', 
            'Bug report'
        ];

        const sortedStatuses = Array.from(statuses).sort((a, b) => {
            const normA = a.trim().toLowerCase();
            const normB = b.trim().toLowerCase();
            
            const indexA = STATUS_ORDER.findIndex(s => s.toLowerCase() === normA);
            const indexB = STATUS_ORDER.findIndex(s => s.toLowerCase() === normB);

            if (indexA !== -1 && indexB !== -1) return indexA - indexB;
            if (indexA !== -1) return -1;
            if (indexB !== -1) return 1;

            return a.localeCompare(b);
        });

        return {
            chartData: Object.values(pivoted),
            statusKeys: sortedStatuses
        };
    }, [data]);

    if (!data || data.length === 0) return <div className="h-full flex items-center justify-center text-slate-400">Sem dados</div>;

    const colors = ['#1E40AF', '#2563EB', '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE', '#CBD5E1'];

    return (
        <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={processedData.chartData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                    <XAxis 
                        dataKey="name" 
                        tick={{fontSize: 11, fill: '#64748B'}} 
                        tickLine={false}
                        axisLine={false}
                    />
                    <YAxis 
                        tick={{fontSize: 11, fill: '#64748B'}} 
                        tickLine={false}
                        axisLine={false}
                    />
                    <Tooltip 
                        cursor={{fill: '#F8FAFC'}}
                        contentStyle={{backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #E2E8F0', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}}
                    />
                    <Legend wrapperStyle={{paddingTop: '10px'}} iconType="circle"/>
                    {processedData.statusKeys.map((status, index) => (
                        <Bar 
                            key={status} 
                            dataKey={status} 
                            fill={colors[index % colors.length]} 
                            radius={[4, 4, 0, 0]}
                        >
                             <LabelList dataKey={status} position="top" style={{ fill: '#64748B', fontSize: '11px' }} />
                        </Bar>
                    ))}
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
};

export default StatusChart;
