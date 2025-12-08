import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const BurndownChart = ({ data }) => {
    if (!data || data.length === 0) return <div className="h-full flex items-center justify-center text-slate-400">Sem dados</div>;

    const formattedData = data.map(item => ({
        ...item,
        date: new Date(item.date).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
    }));

    return (
        <div className="h-[300px] w-full">
             <ResponsiveContainer width="100%" height="100%">
                <LineChart data={formattedData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                    <XAxis 
                        dataKey="date" 
                        stroke="#94A3B8"
                        tick={{fontSize: 11}}
                        tickLine={false}
                        axisLine={false}
                        minTickGap={30}
                    />
                    <YAxis 
                        stroke="#94A3B8"
                        tick={{fontSize: 11}}
                        tickLine={false}
                        axisLine={false}
                    />
                    <Tooltip 
                        contentStyle={{backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #E2E8F0', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}}
                        itemStyle={{color: '#1E293B', fontSize: '12px'}}
                        labelStyle={{color: '#64748B', fontSize: '11px', marginBottom: '4px'}}
                    />
                    <Legend iconType="circle" wrapperStyle={{paddingTop: '10px'}}/>
                    <Line 
                        type="monotone" 
                        dataKey="scope" 
                        name="Escopo Total" 
                        stroke="#1E40AF" 
                        strokeWidth={3} 
                        dot={false} 
                        activeDot={{ r: 6 }} 
                    />
                    <Line 
                        type="monotone" 
                        dataKey="delivered" 
                        name="Entregue" 
                        stroke="#3B82F6" 
                        strokeWidth={3} 
                        dot={false} 
                    />
                </LineChart>
             </ResponsiveContainer>
        </div>
    );
};

export default BurndownChart;