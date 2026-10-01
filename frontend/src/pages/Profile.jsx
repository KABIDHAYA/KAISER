import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { dashboard } from '../api/endpoints';
import LoadingSpinner from '../components/LoadingSpinner';
import { FiUser, FiMail, FiCalendar, FiActivity } from 'react-icons/fi';

const Profile = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await dashboard.getDashboard();
        const dist = res.data.sentiment_distribution || {};
        setStats({
          total: res.data.total_analyses || 0,
          positive: dist.Positive || 0,
          negative: dist.Negative || 0,
          neutral: dist.Neutral || 0,
        });
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (!user) return null;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Profile Settings</h1>
      
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden">
        <div className="p-6 sm:p-8">
          <div className="flex items-center space-x-6">
            <div className="h-24 w-24 bg-indigo-100 dark:bg-indigo-900 rounded-full flex items-center justify-center text-indigo-600 dark:text-indigo-400 text-4xl font-bold uppercase">
              {user.full_name?.charAt(0) || 'U'}
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{user.full_name}</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 flex items-center">
                <FiMail className="mr-1.5" /> {user.email}
              </p>
              {user.created_at && (
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 flex items-center">
                  <FiCalendar className="mr-1.5" /> Member since {new Date(user.created_at).toLocaleDateString()}
                </p>
              )}
            </div>
          </div>
        </div>
        
        <div className="border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 p-6 sm:p-8">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
            <FiActivity className="mr-2" /> Activity Statistics
          </h3>
          
          {loading ? (
            <div className="flex justify-center py-4">
              <LoadingSpinner className="text-indigo-600" />
            </div>
          ) : stats ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-white dark:bg-gray-700 p-4 rounded-lg shadow-sm border border-gray-200 dark:border-gray-600 text-center">
                <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Total Analyses</p>
                <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">{stats.total}</p>
              </div>
              <div className="bg-white dark:bg-gray-700 p-4 rounded-lg shadow-sm border border-gray-200 dark:border-gray-600 text-center">
                <p className="text-xs font-medium text-green-500 dark:text-green-400 uppercase tracking-wide">Positive</p>
                <p className="mt-2 text-3xl font-bold text-green-600 dark:text-green-300">{stats.positive}</p>
              </div>
              <div className="bg-white dark:bg-gray-700 p-4 rounded-lg shadow-sm border border-gray-200 dark:border-gray-600 text-center">
                <p className="text-xs font-medium text-red-500 dark:text-red-400 uppercase tracking-wide">Negative</p>
                <p className="mt-2 text-3xl font-bold text-red-600 dark:text-red-300">{stats.negative}</p>
              </div>
              <div className="bg-white dark:bg-gray-700 p-4 rounded-lg shadow-sm border border-gray-200 dark:border-gray-600 text-center">
                <p className="text-xs font-medium text-yellow-500 dark:text-yellow-400 uppercase tracking-wide">Neutral</p>
                <p className="mt-2 text-3xl font-bold text-yellow-600 dark:text-yellow-300">{stats.neutral}</p>
              </div>
            </div>
          ) : (
            <p className="text-gray-500 dark:text-gray-400">Failed to load statistics.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;
