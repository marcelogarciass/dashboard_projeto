import React from 'react';
import { CheckCircle2, PlusCircle, ArrowUp, ArrowDown } from 'lucide-react';

const DailyKpiCard = ({ title, value, avg, trend, icon: Icon, colorClass }) => {
    const isUp = trend === 'up';
    // Green if Up (Delivered), Red if Down. For simplicity, we assume Up is generally 'Active'
    // User requested "visual indicator comparing with average".
    
    const TrendIcon = isUp ? ArrowUp : ArrowDown;
    const trendColor = isUp ? 'text-green-600' : 'text-red-600';
    const trendBg = isUp ? 'bg-green-50' : 'bg-red-50';
    
    return (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex items-center justify-between">
            <div>
                <p className="text-sm font-medium text-slate-500 mb-1">{title}</p>
                <div className="flex items-baseline gap-2">
                    <h3 className="text-2xl font-bold text-slate-800">{value}</h3>
                    <div className={`flex items-center text-xs font-medium ${trendColor} ${trendBg} px-2 py-0.5 rounded-full`}>
                        <TrendIcon className="w-3 h-3 mr-1" />
                        <span>vs {avg} (7d)</span>
                    </div>
                </div>
            </div>
            <div className={`p-3 rounded-lg ${colorClass}`}>
                <Icon className="w-6 h-6 text-white" />
            </div>
        </div>
    );
};

const DailyKPIs = ({ data }) => {
    if (!data) return null;
    const { delivered, created } = data;

    return (
        <div className="grid grid-cols-1 gap-6 h-full">
            <DailyKpiCard 
                title="Entregues Hoje" 
                value={delivered.value} 
                avg={delivered.avg} 
                trend={delivered.trend}
                icon={CheckCircle2}
                colorClass="bg-emerald-500"
            />
            <DailyKpiCard 
                title="Criados Hoje" 
                value={created.value} 
                avg={created.avg} 
                trend={created.trend}
                icon={PlusCircle}
                colorClass="bg-blue-500"
            />
        </div>
    );
};

export default DailyKPIs;
