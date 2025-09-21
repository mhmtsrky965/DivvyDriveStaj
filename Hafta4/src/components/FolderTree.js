import React, { useState, useEffect, useCallback } from 'react';
import { Folder, FolderOpen, ChevronRight, ChevronDown, X } from 'lucide-react';
import { apiService } from '../services/api';
import { useApp } from '../context/AppContext';
import './FolderTree.css';

const FolderTree = ({ onSelectPath, selectedPath, itemName, onClose }) => {
  const { ticket } = useApp();
  const [expandedFolders, setExpandedFolders] = useState({});
  const [folderTree, setFolderTree] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentSelected, setCurrentSelected] = useState(selectedPath || '');

  const loadRootFolders = useCallback(async () => {
    if (!ticket) return;
    
    setLoading(true);
    try {
      const result = await apiService.getFolders(ticket.ID, '');
      if (result.Sonuc) {
        setFolderTree(result.SonucKlasorListe || []);
      }
    } catch (error) {
      console.error('Error loading root folders:', error);
    } finally {
      setLoading(false);
    }
  }, [ticket]);

  useEffect(() => {
    loadRootFolders();
  }, [loadRootFolders]);

  const loadSubFolders = async (folderPath) => {
    if (!ticket) return [];
    
    try {
      const result = await apiService.getFolders(ticket.ID, folderPath);
      if (result.Sonuc) {
        return result.SonucKlasorListe || [];
      }
    } catch (error) {
      console.error('Error loading subfolders:', error);
    }
    return [];
  };

  const toggleFolder = async (folder, currentPath = '') => {
    const fullPath = currentPath ? `${currentPath}/${folder.Adi}` : folder.Adi;
    
    if (expandedFolders[fullPath]) {
      setExpandedFolders(prev => ({
        ...prev,
        [fullPath]: null
      }));
    } else {
      const subFolders = await loadSubFolders(fullPath);
      setExpandedFolders(prev => ({
        ...prev,
        [fullPath]: subFolders
      }));
    }
  };

  const handleSelectPath = (path) => {
    setCurrentSelected(path);
  };

  const handleConfirm = () => {
    onSelectPath(currentSelected);
  };

  const renderFolder = (folder, currentPath = '', level = 0) => {
    const fullPath = currentPath ? `${currentPath}/${folder.Adi}` : folder.Adi;
    const isExpanded = expandedFolders[fullPath];
    const isSelected = currentSelected === fullPath;

    return (
      <div key={folder.ID} className="folder-tree-item">
        <div 
          className={`folder-row ${isSelected ? 'selected' : ''}`}
          style={{ paddingLeft: `${level * 20 + 10}px` }}
        >
          <button 
            className="expand-button"
            onClick={() => toggleFolder(folder, currentPath)}
          >
            {isExpanded ? 
              <ChevronDown size={16} /> : 
              <ChevronRight size={16} />
            }
          </button>
          
          <div 
            className="folder-content"
            onClick={() => handleSelectPath(fullPath)}
          >
            {isExpanded ? 
              <FolderOpen size={16} color="#4285f4" /> : 
              <Folder size={16} color="#4285f4" />
            }
            <span className="folder-name">{folder.Adi}</span>
          </div>
        </div>
        
        {isExpanded && Array.isArray(isExpanded) && (
          <div className="folder-children">
            {isExpanded.map(subFolder => 
              renderFolder(subFolder, fullPath, level + 1)
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="folder-tree-overlay" onClick={onClose}>
      <div className="folder-tree-modal" onClick={(e) => e.stopPropagation()}>
        <div className="folder-tree-header">
          <h3>📂 Taşınacak Konumu Seçin</h3>
          <button onClick={onClose} className="close-button">
            <X size={20} />
          </button>
        </div>
        
        <div className="folder-tree-info">
          <p><strong>{itemName}</strong> taşınacak. Hedef klasörü seçin:</p>
        </div>
        
        <div className="folder-tree-content">
          <div 
            className={`folder-row root-folder ${currentSelected === '' ? 'selected' : ''}`}
            onClick={() => handleSelectPath('')}
          >
            <div className="folder-content">
              <Folder size={16} color="#4285f4" />
              <span className="folder-name">📁 Anasayfa</span>
            </div>
          </div>
          
          {loading ? (
            <div className="loading">Yükleniyor...</div>
          ) : (
            folderTree.map(folder => renderFolder(folder))
          )}
        </div>
        
        <div className="folder-tree-footer">
          <div className="selected-path">
            <strong>Hedef:</strong> {currentSelected || '📁 Anasayfa'}
          </div>
          <div className="folder-tree-buttons">
            <button onClick={onClose} className="cancel-button">
              ❌ İptal
            </button>
            <button 
              onClick={handleConfirm} 
              className="confirm-button"
              disabled={currentSelected === selectedPath}
            >
              ✅ Bu Konuma Taşı
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FolderTree;