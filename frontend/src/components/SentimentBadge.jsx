import React from 'react';

const SentimentBadge = ({ sentiment, confidence }) => {
  const isPositive = sentiment?.toLowerCase() === 'positive';
  const isNegative = sentiment?.toLowerCase() === 'negative';
  const isNeutral = sentiment?.toLowerCase() === 'neutral';

  const baseClasses = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium';
  
  let colorClasses = 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
  if (isPositive) {
    colorClasses = 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';
  } else if (isNegative) {
    colorClasses = 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';
  } else if (isNeutral) {
    colorClasses = 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400';
  }

  return (
    <span className={`${baseClasses} ${colorClasses}`}>
      {sentiment} {confidence ? `(${confidence}%)` : ''}
    </span>
  );
};

export default SentimentBadge;
