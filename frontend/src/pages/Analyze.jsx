import React, { useState } from 'react';
import { analysis } from '../api/endpoints';
import { toast } from 'react-hot-toast';
import Papa from 'papaparse';
import SentimentBadge from '../components/SentimentBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import { FiUploadCloud, FiDownload } from 'react-icons/fi';

const Analyze = () => {
  const [activeTab, setActiveTab] = useState('single');
  
  // Single Review State
  const [reviewText, setReviewText] = useState('');
  const [singleResult, setSingleResult] = useState(null);
  const [isSingleLoading, setIsSingleLoading] = useState(false);

  // Bulk Analysis State
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewData, setPreviewData] = useState([]);
  const [bulkResult, setBulkResult] = useState(null);
  const [isBulkLoading, setIsBulkLoading] = useState(false);

  const handleSingleAnalyze = async () => {
    if (!reviewText.trim()) {
      toast.error('Please enter a review to analyze');
      return;
    }
    setIsSingleLoading(true);
    try {
      const res = await analysis.analyzeSingle({ review: reviewText });
      setSingleResult(res.data);
      toast.success('Analysis complete');
    } catch (err) {
      toast.error('Failed to analyze review');
    } finally {
      setIsSingleLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!file.name.endsWith('.csv')) {
        toast.error('Please upload a .csv file');
        return;
      }
      setSelectedFile(file);
      Papa.parse(file, {
        header: true,
        preview: 5,
        complete: (results) => {
          setPreviewData(results.data);
        }
      });
    }
  };

  const handleBulkAnalyze = async () => {
    if (!selectedFile) {
      toast.error('Please select a file to upload');
      return;
    }
    setIsBulkLoading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);
    try {
      const res = await analysis.analyzeBulk(formData);
      setBulkResult(res.data);
      toast.success('Bulk analysis complete');
    } catch (err) {
      toast.error('Failed to analyze file');
    } finally {
      setIsBulkLoading(false);
    }
  };

  const exportBulkCSV = () => {
    if (!bulkResult || !bulkResult.results) return;
    const csv = Papa.unparse(bulkResult.results);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'analysis_results.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-6 border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('single')}
            className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'single'
                ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            Single Review
          </button>
          <button
            onClick={() => setActiveTab('bulk')}
            className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'bulk'
                ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            Bulk Analysis
          </button>
        </nav>
      </div>

      {activeTab === 'single' ? (
        <div className="space-y-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <label htmlFor="review" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Enter your text below
            </label>
            <textarea
              id="review"
              rows={6}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white p-3 resize-none"
              placeholder="e.g., The product was amazing and the support was extremely helpful!"
              value={reviewText}
              onChange={(e) => setReviewText(e.target.value)}
            />
            <div className="mt-4 flex space-x-3">
              <button
                onClick={handleSingleAnalyze}
                disabled={isSingleLoading || !reviewText.trim()}
                className="flex-1 sm:flex-none inline-flex justify-center items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
              >
                {isSingleLoading ? <LoadingSpinner className="w-5 h-5 mr-2" /> : null}
                Analyze Review
              </button>
              <button
                onClick={() => { setReviewText(''); setSingleResult(null); }}
                className="inline-flex justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600"
              >
                Clear
              </button>
            </div>
          </div>

          {singleResult && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden animate-fade-in-up">
              <div className="px-6 py-5 border-b border-gray-200 dark:border-gray-700">
                <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">Analysis Results</h3>
              </div>
              <div className="p-6 space-y-6">
                <div>
                  <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Sentiment</h4>
                  <div className="flex items-center space-x-4">
                    <SentimentBadge sentiment={singleResult.sentiment} confidence={null} />
                    {singleResult.confidence && (
                      <div className="flex-1 max-w-xs">
                        <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mb-1">
                          <span>Confidence</span>
                          <span>{parseFloat(singleResult.confidence).toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2 dark:bg-gray-700">
                          <div 
                            className={`h-2 rounded-full ${singleResult.sentiment.toLowerCase() === 'positive' ? 'bg-green-500' : singleResult.sentiment.toLowerCase() === 'negative' ? 'bg-red-500' : 'bg-yellow-500'}`}
                            style={{ width: `${parseFloat(singleResult.confidence)}%` }}
                          ></div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {singleResult.keywords && singleResult.keywords.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Extracted Keywords</h4>
                    <div className="flex flex-wrap gap-2">
                      {singleResult.keywords.map((kw, idx) => (
                        <span key={idx} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-300">
                          {kw.word}
                          {kw.weight && <span className="ml-1 opacity-70">({kw.weight.toFixed(2)})</span>}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div 
              className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-12 text-center hover:border-indigo-500 dark:hover:border-indigo-400 transition-colors"
            >
              <FiUploadCloud className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500 mb-4" />
              <div className="text-sm text-gray-600 dark:text-gray-400">
                <label htmlFor="file-upload" className="relative cursor-pointer bg-transparent rounded-md font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400">
                  <span>Upload a file</span>
                  <input id="file-upload" name="file-upload" type="file" accept=".csv" className="sr-only" onChange={handleFileChange} />
                </label>
                <p className="pl-1 inline">or drag and drop</p>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">CSV files only</p>
            </div>

            {selectedFile && (
              <div className="mt-4 flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-md border border-gray-200 dark:border-gray-700">
                <span className="text-sm text-gray-700 dark:text-gray-300 font-medium truncate pr-4">{selectedFile.name}</span>
                <button
                  onClick={handleBulkAnalyze}
                  disabled={isBulkLoading}
                  className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                >
                  {isBulkLoading ? <LoadingSpinner className="w-4 h-4 mr-1.5" /> : null}
                  Analyze File
                </button>
              </div>
            )}

            {previewData.length > 0 && !bulkResult && (
              <div className="mt-6">
                <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">Preview</h4>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700 text-sm">
                    <thead>
                      <tr>
                        {Object.keys(previewData[0]).map((key) => (
                          <th key={key} className="px-3 py-2 bg-gray-50 dark:bg-gray-800 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{key}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-800">
                      {previewData.map((row, i) => (
                        <tr key={i}>
                          {Object.values(row).map((val, j) => (
                            <td key={j} className="px-3 py-2 text-gray-500 dark:text-gray-400 truncate max-w-xs">{val}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>

          {bulkResult && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
              <div className="px-6 py-5 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
                <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">Bulk Analysis Results</h3>
                <button
                  onClick={exportBulkCSV}
                  className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600 dark:hover:bg-gray-600"
                >
                  <FiDownload className="mr-2" /> Export CSV
                </button>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div className="bg-gray-50 dark:bg-gray-700/50 p-4 rounded-lg">
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Analyzed</p>
                    <p className="mt-1 text-2xl font-semibold text-gray-900 dark:text-white">{bulkResult.summary.total}</p>
                  </div>
                  <div className="bg-green-50 dark:bg-green-900/10 p-4 rounded-lg">
                    <p className="text-sm font-medium text-green-600 dark:text-green-400">Positive</p>
                    <p className="mt-1 text-2xl font-semibold text-green-700 dark:text-green-300">
                      {bulkResult.summary.positive} <span className="text-sm font-normal text-green-600/70">({((bulkResult.summary.positive/bulkResult.summary.total)*100).toFixed(0)}%)</span>
                    </p>
                  </div>
                  <div className="bg-red-50 dark:bg-red-900/10 p-4 rounded-lg">
                    <p className="text-sm font-medium text-red-600 dark:text-red-400">Negative</p>
                    <p className="mt-1 text-2xl font-semibold text-red-700 dark:text-red-300">
                      {bulkResult.summary.negative} <span className="text-sm font-normal text-red-600/70">({((bulkResult.summary.negative/bulkResult.summary.total)*100).toFixed(0)}%)</span>
                    </p>
                  </div>
                  <div className="bg-yellow-50 dark:bg-yellow-900/10 p-4 rounded-lg">
                    <p className="text-sm font-medium text-yellow-600 dark:text-yellow-400">Neutral</p>
                    <p className="mt-1 text-2xl font-semibold text-yellow-700 dark:text-yellow-300">
                      {bulkResult.summary.neutral} <span className="text-sm font-normal text-yellow-600/70">({((bulkResult.summary.neutral/bulkResult.summary.total)*100).toFixed(0)}%)</span>
                    </p>
                  </div>
                </div>

                <div className="overflow-x-auto border border-gray-200 dark:border-gray-700 rounded-lg">
                  <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                    <thead className="bg-gray-50 dark:bg-gray-800">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">#</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Review Text</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Sentiment</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Confidence</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-800">
                      {bulkResult.results.slice(0, 10).map((row, idx) => (
                        <tr key={idx}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{idx + 1}</td>
                          <td className="px-6 py-4 text-sm text-gray-900 dark:text-gray-300">
                            <div className="truncate max-w-md" title={row.review}>{row.review}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <SentimentBadge sentiment={row.sentiment} />
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                            {row.confidence ? `${parseFloat(row.confidence).toFixed(1)}%` : '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {bulkResult.results.length > 10 && (
                    <div className="bg-gray-50 dark:bg-gray-800 px-6 py-3 text-center text-sm text-gray-500 dark:text-gray-400">
                      Showing first 10 results. Export CSV to view all.
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Analyze;
