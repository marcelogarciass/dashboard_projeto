import React, { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

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

        return {
            chartData: Object.values(pivoted),
            statusKeys: Array.from(statuses)
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
                        />
                    ))}
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
};

export default StatusChart;
