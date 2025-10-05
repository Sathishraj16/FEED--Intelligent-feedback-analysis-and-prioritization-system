"use client";

import { useState, useRef } from "react";
import { uploadCsv, getImportStatus, type CsvUploadResponse, type ImportStatus } from "@/lib/api";

export default function CsvUpload() {
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<CsvUploadResponse | null>(null);
  const [importStatus, setImportStatus] = useState<ImportStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
      setError('Please select a CSV file');
      return;
    }

    setUploading(true);
    setError(null);
    setUploadResult(null);

    try {
      const result = await uploadCsv(file);
      setUploadResult(result);
      
      // Refresh import status after successful upload
      const status = await getImportStatus();
      setImportStatus(status);
    } catch (err: any) {
      setError(err.message || 'Upload failed');
    } finally {
      setUploading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const loadImportStatus = async () => {
    try {
      const status = await getImportStatus();
      setImportStatus(status);
    } catch (err: any) {
      setError(err.message || 'Failed to load import status');
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Import App Store Reviews</h2>
        <button
          onClick={loadImportStatus}
          className="text-sm text-blue-600 hover:text-blue-800 font-medium"
        >
          Refresh Status
        </button>
      </div>

      {/* Import Status */}
      {importStatus && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-gray-50 rounded-lg">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{importStatus.total_feedback}</div>
            <div className="text-sm text-gray-600">Total Feedback</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{importStatus.app_store_reviews}</div>
            <div className="text-sm text-gray-600">App Store Reviews</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{importStatus.recent_imports_24h}</div>
            <div className="text-sm text-gray-600">Imported (24h)</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-600">{importStatus.other_sources}</div>
            <div className="text-sm text-gray-600">Other Sources</div>
          </div>
        </div>
      )}

      {/* Upload Section */}
      <div className="space-y-4">
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
          <div className="space-y-2">
            <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
              <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            <div className="text-sm text-gray-600">
              <label htmlFor="csv-upload" className="cursor-pointer">
                <span className="font-medium text-blue-600 hover:text-blue-500">Upload a CSV file</span>
                <span> or drag and drop</span>
              </label>
              <input
                ref={fileInputRef}
                id="csv-upload"
                name="csv-upload"
                type="file"
                accept=".csv"
                className="sr-only"
                onChange={handleFileSelect}
                disabled={uploading}
              />
            </div>
            <p className="text-xs text-gray-500">CSV files only</p>
          </div>
        </div>

        {/* Expected Format Info */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-blue-900 mb-2">Expected CSV Format</h3>
          <div className="text-xs text-blue-800 space-y-1">
            <p><strong>Auto-detected columns:</strong></p>
            <ul className="list-disc list-inside space-y-0.5 ml-2">
              <li><strong>Review text:</strong> 'review', 'content', 'text', 'comment', 'feedback', 'body', 'message'</li>
              <li><strong>Rating:</strong> 'rating', 'score', 'stars', 'star' (optional)</li>
              <li><strong>Title:</strong> 'title', 'subject', 'headline', 'summary' (optional)</li>
              <li><strong>Date:</strong> 'date', 'created', 'submitted', 'time', 'timestamp' (optional)</li>
              <li><strong>App Version:</strong> 'version', 'app_version', 'build' (optional)</li>
              <li><strong>Reviewer:</strong> 'reviewer', 'user', 'author', 'name' (optional)</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Upload Progress */}
      {uploading && (
        <div className="flex items-center space-x-3 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
          <span className="text-sm text-blue-800">Uploading and processing CSV...</span>
        </div>
      )}

      {/* Upload Result */}
      {uploadResult && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-start space-x-3">
            <svg className="h-5 w-5 text-green-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <div className="flex-1">
              <h3 className="text-sm font-medium text-green-900">{uploadResult.message}</h3>
              <div className="mt-2 text-sm text-green-800">
                <p><strong>File:</strong> {uploadResult.filename}</p>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-2">
                  <div>
                    <span className="font-medium">Imported:</span> {uploadResult.stats.imported}
                  </div>
                  <div>
                    <span className="font-medium">Skipped:</span> {uploadResult.stats.skipped}
                  </div>
                  <div>
                    <span className="font-medium">Errors:</span> {uploadResult.stats.errors}
                  </div>
                  <div>
                    <span className="font-medium">Total:</span> {uploadResult.stats.total_processed}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start space-x-3">
            <svg className="h-5 w-5 text-red-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <div>
              <h3 className="text-sm font-medium text-red-900">Upload Error</h3>
              <p className="text-sm text-red-800 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
