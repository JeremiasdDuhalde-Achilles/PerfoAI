import { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import {
  FileText,
  CheckCircle,
  Clock,
  DollarSign,
  TrendingUp,
  AlertCircle,
} from 'lucide-react';
import { invoicesAPI } from '../services/api';

const MetricCard = ({ title, value, subtitle, icon: Icon, color, trend }) => (
  <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
    <div className="flex items-center justify-between mb-4">
      <div className={`p-3 rounded-lg ${color}`}>
        <Icon className="w-6 h-6 text-white" />
      </div>
      {trend && (
        <div className="flex items-center text-green-600 text-sm font-medium">
          <TrendingUp className="w-4 h-4 mr-1" />
          {trend}%
        </div>
      )}
    </div>
    <h3 className="text-2xl font-bold text-gray-900 mb-1">{value}</h3>
    <p className="text-sm font-medium text-gray-600">{title}</p>
    {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
  </div>
);

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMetrics();
  }, []);

  const loadMetrics = async () => {
    try {
      const response = await invoicesAPI.getDashboardMetrics();
      setMetrics(response.data);
    } catch (error) {
      console.error('Failed to load metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-gray-500">Loading dashboard...</div>
      </div>
    );
  }

  // Sample data for charts
  const weeklyData = [
    { day: 'Mon', invoices: 12, touchless: 10 },
    { day: 'Tue', invoices: 15, touchless: 13 },
    { day: 'Wed', invoices: 18, touchless: 16 },
    { day: 'Thu', invoices: 14, touchless: 12 },
    { day: 'Fri', invoices: 16, touchless: 14 },
  ];

  const statusData = [
    { name: 'Approved', value: 45, color: '#10b981' },
    { name: 'Pending', value: 25, color: '#f59e0b' },
    { name: 'Clarification', value: 5, color: '#ef4444' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">
            AI-powered invoice processing analytics
          </p>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <MetricCard
          title="Incoming Invoices"
          value={metrics?.incoming_invoices || 0}
          subtitle="Last 30 days"
          icon={FileText}
          color="bg-blue-500"
          trend={12}
        />
        <MetricCard
          title="Touchless Bookings"
          value={`${metrics?.touchless_bookings || 0}%`}
          subtitle="Auto-processed rate"
          icon={CheckCircle}
          color="bg-green-500"
          trend={5}
        />
        <MetricCard
          title="Pending Clarifications"
          value={metrics?.pending_clarifications || 0}
          subtitle="Requiring attention"
          icon={AlertCircle}
          color="bg-orange-500"
        />
        <MetricCard
          title="Days Payable Outstanding"
          value={`${metrics?.days_payable_outstanding || 0}`}
          subtitle="Average payment days"
          icon={Clock}
          color="bg-purple-500"
        />
        <MetricCard
          title="Realized Cash Discounts"
          value={`${metrics?.realized_cash_discounts || 0}%`}
          subtitle="Early payment savings"
          icon={DollarSign}
          color="bg-teal-500"
          trend={3}
        />
        <MetricCard
          title="Invoice Cycle Time"
          value={`${metrics?.invoice_cycle_time || 0} days`}
          subtitle="Average processing time"
          icon={TrendingUp}
          color="bg-indigo-500"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Weekly Invoice Processing */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Weekly Invoice Processing
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={weeklyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="day" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip />
              <Legend />
              <Bar
                dataKey="invoices"
                fill="#3b82f6"
                name="Total Invoices"
                radius={[8, 8, 0, 0]}
              />
              <Bar
                dataKey="touchless"
                fill="#10b981"
                name="Touchless"
                radius={[8, 8, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Invoice Status Distribution */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Invoice Status Distribution
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={statusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) =>
                  `${name} ${(percent * 100).toFixed(0)}%`
                }
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {statusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Processing Efficiency */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Processing Efficiency Trend
        </h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart
            data={[
              { month: 'Jan', efficiency: 75 },
              { month: 'Feb', efficiency: 78 },
              { month: 'Mar', efficiency: 82 },
              { month: 'Apr', efficiency: 85 },
              { month: 'May', efficiency: 88 },
              { month: 'Jun', efficiency: 92 },
            ]}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="month" stroke="#6b7280" />
            <YAxis stroke="#6b7280" />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="efficiency"
              stroke="#3b82f6"
              strokeWidth={3}
              dot={{ fill: '#3b82f6', r: 6 }}
              name="Touchless Rate (%)"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
