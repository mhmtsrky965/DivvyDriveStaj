import React, { useState, useEffect } from 'react';
import { X, Upload, AlertCircle, CheckCircle } from 'lucide-react';
import { apiService } from '../services/api';
import { FileUtils } from '../utils/fileUtils';
import { useApp } from '../context/AppContext';
import './FileUploader.css';

const FileUploader = ({ onClose, onUploadComplete }) => {
  const { ticket, currentPath } = useApp();
  const [dragOver, setDragOver] = useState(false);
  const [uploads, setUploads] = useState([]);
  const [allCompleted, setAllCompleted] = useState(false);

  useEffect(() => {
    if (uploads.length > 0) {
      const completedUploads = uploads.filter(u => u.status === 'completed');
      const errorUploads = uploads.filter(u => u.status === 'error');
      const totalFinished = completedUploads.length + errorUploads.length;
      
      if (totalFinished === uploads.length && totalFinished > 0) {
        setAllCompleted(true);
        
        setTimeout(() => {
          if (completedUploads.length > 0) {
            alert(`🎉 ${completedUploads.length} dosya başarıyla yüklendi!`);
            onUploadComplete();
          }
          onClose();
        }, 2000);
      }
    }
  }, [uploads, onClose, onUploadComplete]);

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    handleFiles(files);
  };

  const handleFiles = async (files) => {
    console.log('=== FILES SELECTED ===');
    console.log('File count:', files.length);
    
    const newUploads = files.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      name: file.name,
      size: file.size,
      progress: 0,
      status: 'waiting',
      error: null
    }));

    setUploads(prev => [...prev, ...newUploads]);
    setAllCompleted(false);
    
    newUploads.forEach(upload => uploadFile(upload));
  };

  const uploadFile = async (upload) => {
    try {
      setUploads(prev => prev.map(u => 
        u.id === upload.id ? { ...u, status: 'uploading', progress: 5 } : u
      ));

      const { file } = upload;
      const MB = 1024 * 1024;

      if (file.size <= MB) {
        await uploadSmallFile(upload);
      } else {
        await uploadLargeFile(upload);
      }

      setUploads(prev => prev.map(u => 
        u.id === upload.id ? { ...u, status: 'completed', progress: 100 } : u
      ));

    } catch (error) {
      console.error('Upload error:', error);
      setUploads(prev => prev.map(u => 
        u.id === upload.id ? { 
          ...u, 
          status: 'error', 
          progress: 0,
          error: error.response?.data?.Mesaj || error.message || 'Upload failed' 
        } : u
      ));
    }
  };

  const uploadSmallFile = async (upload) => {
    const { file } = upload;
    
    try {
      console.log('=== SMALL FILE UPLOAD ===');
      
      setUploads(prev => prev.map(u => 
        u.id === upload.id ? { ...u, progress: 20 } : u
      ));
      
      const hash = await FileUtils.calculateMD5Hash(file);
      console.log('Calculated MD5 hash:', hash);
      

      setUploads(prev => prev.map(u => 
        u.id === upload.id ? { ...u, progress: 50 } : u
      ));
      
      const result = await apiService.uploadFileDirect(
        ticket.ID,
        file.name,
        currentPath,
        hash,
        file
      );

      console.log('Upload result:', result);

      if (!result.Sonuc) {
        throw new Error(result.Mesaj || 'Direct upload failed');
      }
    } catch (error) {
      console.error('Small file upload error:', error);
      throw error;
    }
  };

  const uploadLargeFile = async (upload) => {
    const { file } = upload;
    const MB = 1024 * 1024;
    const chunks = FileUtils.splitFile(file, MB);
    
    try {
      console.log('=== LARGE FILE UPLOAD ===');
      
      setUploads(prev => prev.map(u => 
        u.id === upload.id ? { ...u, progress: 10 } : u
      ));
      
      const metaResult = await apiService.createFileMetaData(
        ticket.ID,
        file.name,
        chunks.length,
        MB
      );

      console.log('Metadata result:', metaResult);

      if (!metaResult.Sonuc) {
        throw new Error(metaResult.Mesaj || 'Failed to create file metadata');
      }

      let tempKlasorID = null;
      
      if (metaResult.ID) {
        tempKlasorID = metaResult.ID;
      } else if (metaResult.TempKlasorID) {
        tempKlasorID = metaResult.TempKlasorID;
      } else if (metaResult.tempKlasorID) {
        tempKlasorID = metaResult.tempKlasorID;
      } else if (metaResult.Mesaj && metaResult.Mesaj.includes('-')) {
        const guidMatch = metaResult.Mesaj.match(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i);
        if (guidMatch) {
          tempKlasorID = guidMatch[0];
        }
      }

      console.log('Using temp folder ID:', tempKlasorID);

      if (!tempKlasorID) {
        throw new Error('Temp klasör ID bulunamadı. Response: ' + JSON.stringify(metaResult));
      }

      for (let i = 0; i < chunks.length; i++) {
        const chunk = chunks[i];
        
        console.log(`=== CHUNK ${i + 1}/${chunks.length} ===`);
        
        const chunkHash = await FileUtils.calculateMD5Hash(chunk);
        console.log('Chunk MD5 hash:', chunkHash);
        
        const chunkResult = await apiService.uploadFilePart(
          ticket.ID,
          tempKlasorID,
          chunkHash,
          i + 1,
          chunk
        );

        console.log(`Chunk ${i + 1} result:`, chunkResult);

        if (!chunkResult.Sonuc) {
          throw new Error(`Chunk ${i + 1} upload failed: ${chunkResult.Mesaj}`);
        }

        const progress = 10 + ((i + 1) / chunks.length) * 70;
        setUploads(prev => prev.map(u => 
          u.id === upload.id ? { ...u, progress } : u
        ));
      }

      setUploads(prev => prev.map(u => 
        u.id === upload.id ? { ...u, progress: 90 } : u
      ));

      console.log('=== PUBLISHING FILE ===');
      const publishResult = await apiService.publishFile(
        ticket.ID,
        tempKlasorID,
        file.name,
        currentPath
      );

      console.log('Publish result:', publishResult);

      if (!publishResult.Sonuc) {
        throw new Error(publishResult.Mesaj || 'Failed to publish file');
      }
      
    } catch (error) {
      console.error('Large file upload error:', error);
      throw error;
    }
  };

  const handleClose = (e) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    
    const hasActiveUploads = uploads.some(u => u.status === 'uploading');
    if (hasActiveUploads && !window.confirm('Yükleme devam ediyor. Kapatmak istediğinizden emin misiniz?')) {
      return;
    }
    
    onClose();
  };

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      handleClose(e);
    }
  };

  return (
    <div className="file-uploader-overlay" onClick={handleOverlayClick}>
      <div className="file-uploader" onClick={(e) => e.stopPropagation()}>
        <div className="uploader-header">
          <h3>Dosya Yükle</h3>
          <button 
            onClick={handleClose} 
            className="close-button visible" 
            type="button"
            aria-label="Kapat"
          >
            <X size={24} strokeWidth={2} />
          </button>
        </div>

        {!allCompleted && (
          <div
            className={`drop-zone ${dragOver ? 'drag-over' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => document.getElementById('file-input').click()}
          >
            <Upload size={48} />
            <p>Dosyaları buraya sürükleyin veya tıklayın</p>
            <span className="drop-zone-hint">
              1MB'dan büyük dosyalar otomatik olarak parçalanacak
            </span>
            <input
              id="file-input"
              type="file"
              multiple
              onChange={handleFileSelect}
              style={{ display: 'none' }}
              accept="*/*"
            />
          </div>
        )}

        {uploads.length > 0 && (
          <div className="uploads-list">
            <h4>
              Yüklenen Dosyalar ({uploads.length})
              {allCompleted && <span style={{ color: '#28a745', marginLeft: '10px' }}>✅ Tamamlandı</span>}
            </h4>
            {uploads.map(upload => (
              <div key={upload.id} className={`upload-item ${upload.status}`}>
                <div className="upload-info">
                  <div className="upload-name-container">
                    <span className="upload-status-icon">
                      {upload.status === 'completed' ? <CheckCircle size={20} color="#28a745" /> :
                       upload.status === 'error' ? <AlertCircle size={20} color="#dc3545" /> : 
                       <div className="spinner"></div>}
                    </span>
                    <span className="upload-name" title={upload.name}>
                      {upload.name}
                    </span>
                  </div>
                  <span className="upload-size">
                    {FileUtils.formatFileSize(upload.size)}
                  </span>
                </div>
                
                <div className="upload-progress">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill"
                      style={{ 
                        width: `${upload.progress}%`,
                        backgroundColor: 
                          upload.status === 'completed' ? '#28a745' :
                          upload.status === 'error' ? '#dc3545' :
                          '#667eea'
                      }}
                    />
                  </div>
                  <span className="progress-text">
                    {upload.status === 'waiting' && 'Bekliyor...'}
                    {upload.status === 'uploading' && `${Math.round(upload.progress)}%`}
                    {upload.status === 'completed' && 'Tamamlandı'}
                    {upload.status === 'error' && 'Hata'}
                  </span>
                </div>

                {upload.status === 'error' && upload.error && (
                  <div className="upload-error">
                    <AlertCircle size={16} />
                    {upload.error}
                  </div>
                )}
              </div>
            ))}
            
                        {allCompleted && (
              <div className="upload-complete-message">
                <CheckCircle size={48} color="#28a745" />
                <p>Yükleme işlemi tamamlandı!</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default FileUploader;