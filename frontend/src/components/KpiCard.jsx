import React from 'react';

const KpiCard = ({ title, value, subtext, type = "default", icon: Icon }) => {
    const colors = {
        default: "text-slate-800",
        primary: "text-blue-600",
        danger: "text-red-600",
        success: "text-emerald-600"
    };

    return (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-2">
                <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider">{title}</h3>
                {Icon && <Icon className="text-slate-400 h-5 w-5" />}
            </div>
            <div className={`text-3xl font-bold ${colors[type]}`}>{value}</div>
            {subtext && <div className="text-xs text-slate-400 mt-2 font-medium">{subtext}</div>}
        </div>
    );
};

export default KpiCard;