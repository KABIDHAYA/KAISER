import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { dashboard } from '../api/endpoints';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import SentimentBadge from '../components/SentimentBadge';
import LoadingSpinner from '../components/LoadingSpinner';

const COLORS = {
  Positive: '#10B981',
  Negative: '#EF4444',
  Neutral: '#F59E0B'
};

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const res = await dashboard.getDashboard();
      setData(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <LoadingSpinner className="w-10 h-10 text-indigo-600" />
      </div>
    );
  }

  if (!data || data.total_analyses === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center py-20">
        <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">Welcome to ReviewSense</h2>
        <p className="text-gray-500 dark:text-gray-400 mb-6">You haven't analyzed any reviews yet.</p>
        <Link
          to="/analyze"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
        >
          Start Analyzing Reviews
        </Link>
      </div>
    );
  }

  const pieData = [
    { name: 'Positive', value: data.sentiment_distribution?.Positive || 0 },
    { name: 'Negative', value: data.sentiment_distribution?.Negative || 0 },
    { name: 'Neutral', value: data.sentiment_distribution?.Neutral || 0 },
  ].filter(d => d.value > 0);

  // Combine positive and negative words for word cloud
  const wordCloudData = [
    ...(data.top_positive_words || []).map(kw => ({ text: kw.word, value: kw.count })),
    ...(data.top_negative_words || []).map(kw => ({ text: kw.word, value: kw.count })),
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <div className="text-sm text-gray-500 dark:text-gray-400">
          Total Analyses: <span className="font-semibold text-gray-900 dark:text-white">{data.total_analyses}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sentiment Distribution */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Sentiment Distribution</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[entry.name]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Word Cloud - simple styled word display */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Common Keywords</h2>
          <div className="h-64 flex flex-wrap items-center justify-center gap-3 overflow-hidden">
            {wordCloudData.length > 0 ? (
              wordCloudData.map((w, i) => (
                <span
                  key={i}
                  className="inline-block px-3 py-1 rounded-full font-semibold transition-transform hover:scale-110"
                  style={{
                    fontSize: `${Math.max(12, Math.min(32, 12 + w.value * 4))}px`,
                    color: ['#6366f1', '#10B981', '#EF4444', '#F59E0B', '#8B5CF6', '#EC4899', '#14B8A6', '#F97316'][i % 8],
                    opacity: 0.7 + (w.value / Math.max(...wordCloudData.map(d => d.value))) * 0.3,
                  }}
                >
                  {w.text}
                </span>
              ))
            ) : (
              <p className="text-center text-gray-500 dark:text-gray-400">No keywords available</p>
            )}
          </div>
        </div>

        {/* Top Positive Words */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Top Positive Words</h2>
          <div className="h-64">
            {data.top_positive_words && data.top_positive_words.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.top_positive_words} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <XAxis type="number" />
                  <YAxis dataKey="word" type="category" width={80} tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#10B981" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">No data yet</div>
            )}
          </div>
        </div>

        {/* Top Negative Words */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Top Negative Words</h2>
          <div className="h-64">
            {data.top_negative_words && data.top_negative_words.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.top_negative_words} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <XAxis type="number" />
                  <YAxis dataKey="word" type="category" width={80} tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#EF4444" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">No data yet</div>
            )}
          </div>
        </div>
      </div>

      {/* Recent Analyses */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white">Recent Analyses</h2>
        </div>
        <ul className="divide-y divide-gray-200 dark:divide-gray-700">
          {data.recent_analyses.map((item) => (
            <li key={item.id} className="px-6 py-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
              <div className="flex-1 min-w-0 pr-4">
                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {item.review_text}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {new Date(item.created_at).toLocaleDateString()} · {item.analysis_type}
                </p>
              </div>
              <div className="flex-shrink-0">
                <SentimentBadge sentiment={item.sentiment} confidence={parseFloat(item.confidence).toFixed(1)} />
              </div>
            </li>
          ))}
          {data.recent_analyses.length === 0 && (
            <li className="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
              No recent analyses found.
            </li>
          )}
        </ul>
      </div>
    </div>
  );
};

export default Dashboard;
