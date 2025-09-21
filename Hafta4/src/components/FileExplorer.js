import React, { useState, useEffect, useCallback } from 'react';
import { 
  Folder, 
  File, 
  MoreHorizontal, 
  ArrowLeft, 
  Plus,
  Upload,
  FileText,
  FolderPlus,
  Search,
  X,
  LogOut,
  Sun,
  Moon,
  Trash2,
  Move,
  Download,
  XCircle
} from 'lucide-react';
import { apiService } from '../services/api';
import { useApp } from '../context/AppContext';
import FileUploader from './FileUploader';
import ContextMenu from './ContextMenu';
import Modal from './Modal';
import FolderTree from './FolderTree';
import './FileExplorer.css';

const getUniqueId = (item, type) => `${type}-${item.ID}`;

const FileExplorer = () => {
  const { ticket, currentPath, setCurrentPath, logout, theme, toggleTheme } = useApp();
  const [showUploader, setShowUploader] = useState(false);
  const [showCreateMenu, setShowCreateMenu] = useState(false);
  const [contextMenu, setContextMenu] = useState({ show: false, x: 0, y: 0, item: null, type: null });
  const [modal, setModal] = useState({ show: false, type: '', item: null, itemType: null });
  const [newName, setNewName] = useState('');
  const [showFolderTree, setShowFolderTree] = useState(false);
  const [moveItem, setMoveItem] = useState(null);
  const [moveType, setMoveType] = useState('');
  const [loading, setLoading] = useState(true);
  
  const [searchTerm, setSearchTerm] = useState('');
  const [allFolders, setAllFolders] = useState([]);
  const [allFiles, setAllFiles] = useState([]);
  const [displayedFolders, setDisplayedFolders] = useState([]);
  const [displayedFiles, setDisplayedFiles] = useState([]);

  const [selectedItems, setSelectedItems] = useState(new Set());
  const [lastSelectedItem, setLastSelectedItem] = useState(null);

  const loadContent = useCallback(async () => {
    if (!ticket) return;
    
    setLoading(true);
    setSelectedItems(new Set());
    setLastSelectedItem(null);

    try {
      const [foldersResult, filesResult] = await Promise.all([
        apiService.getFolders(ticket.ID, currentPath),
        apiService.getFiles(ticket.ID, currentPath)
      ]);

      const foldersList = foldersResult.Sonuc ? (foldersResult.SonucKlasorListe || []) : [];
      const filesList = filesResult.Sonuc ? (filesResult.SonucDosyaListe || []) : [];
      
      setAllFolders(foldersList);
      setAllFiles(filesList);

    } catch (error) {
      console.error('Error loading content:', error);
      setAllFolders([]);
      setAllFiles([]);
    } finally {
      setLoading(false);
    }
  }, [ticket, currentPath]);

  useEffect(() => {
    loadContent();
  }, [loadContent]);

  useEffect(() => {
    if (loading) return;

    if (!searchTerm.trim()) {
      setDisplayedFolders(allFolders);
      setDisplayedFiles(allFiles);
    } else {
      const searchLower = searchTerm.toLowerCase();
      setDisplayedFolders(allFolders.filter(folder => folder.Adi.toLowerCase().includes(searchLower)));
      setDisplayedFiles(allFiles.filter(file => file.Adi.toLowerCase().includes(searchLower)));
    }
  }, [searchTerm, allFolders, allFiles, loading]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      const fabContainer = document.querySelector('.fab-container');
      if (fabContainer && !fabContainer.contains(event.target)) {
        setShowCreateMenu(false);
      }
    };
    if (showCreateMenu) document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showCreateMenu]);
  
  const handleItemClick = (e, item, type) => {
    e.stopPropagation();
    
    const currentItems = [
      ...displayedFolders.map(f => ({ ...f, uniqueId: getUniqueId(f, 'folder') })),
      ...displayedFiles.map(f => ({ ...f, uniqueId: getUniqueId(f, 'file') })),
    ];
    const uniqueId = getUniqueId(item, type);

    if (e.shiftKey && lastSelectedItem) {
        const newSelection = new Set(selectedItems);
        const lastIndex = currentItems.findIndex(i => i.uniqueId === lastSelectedItem);
        const currentIndex = currentItems.findIndex(i => i.uniqueId === uniqueId);
        
        if (lastIndex > -1 && currentIndex > -1) {
            const start = Math.min(lastIndex, currentIndex);
            const end = Math.max(lastIndex, currentIndex);
            for (let i = start; i <= end; i++) {
                newSelection.add(currentItems[i].uniqueId);
            }
        }
        setSelectedItems(newSelection);
    } else if (e.ctrlKey || e.metaKey) {
        const newSelection = new Set(selectedItems);
        if (newSelection.has(uniqueId)) {
            newSelection.delete(uniqueId);
        } else {
            newSelection.add(uniqueId);
        }
        setSelectedItems(newSelection);
        setLastSelectedItem(uniqueId);
    } else {
        setSelectedItems(new Set([uniqueId]));
        setLastSelectedItem(uniqueId);
    }
  };

  const handleFolderDoubleClick = (folder) => {
    const newPath = currentPath ? `${currentPath}/${folder.Adi}` : folder.Adi;
    setCurrentPath(newPath);
    setSearchTerm('');
  };

  const clearSelection = (e) => {
    if (e.target === e.currentTarget) {
        setSelectedItems(new Set());
        setLastSelectedItem(null);
    }
  };

  const handleBackClick = () => {
    const pathParts = currentPath.split('/');
    pathParts.pop();
    const newPath = pathParts.join('/');
    setCurrentPath(newPath);
    setSearchTerm('');
  };

  const handleContextMenu = (e, item, type) => {
    e.preventDefault();
    e.stopPropagation();
    const uniqueId = getUniqueId(item, type);
    
    if (!selectedItems.has(uniqueId)) {
      setSelectedItems(new Set([uniqueId]));
      setLastSelectedItem(uniqueId);
    }

    setShowCreateMenu(false);
    setContextMenu({ show: true, x: e.clientX, y: e.clientY, item, type });
  };

  const handleContextMenuAction = async (action) => {
    const { item, type } = contextMenu;
    setContextMenu({ show: false, x: 0, y: 0, item: null, type: null });
    
    switch (action) {
      case 'rename':
        setModal({ show: true, type: 'rename', item, itemType: type });
        setNewName(item.Adi);
        break;
      case 'delete':
        setModal({ show: true, type: 'delete', item, itemType: type });
        break;
      case 'move':
        setMoveItem(item);
        setMoveType(type);
        setShowFolderTree(true);
        break;
      case 'download':
        if (type === 'file') await handleDownloadFile(item);
        break;
      default: console.log('Unknown action:', action);
    }
  };

  const getSelectedItemsDetails = () => {
    return Array.from(selectedItems).map(uniqueId => {
      const [type, ...idParts] = uniqueId.split('-');
      const id = idParts.join('-'); 

      if (type === 'folder') {
        const folder = allFolders.find(f => String(f.ID) === id);
        if (folder) return { ...folder, type: 'folder' };
      } else if (type === 'file') {
        const file = allFiles.find(f => String(f.ID) === id);
        if (file) return { ...file, type: 'file' };
      }
      return null;
    }).filter(Boolean);
  };

  const handleDeleteMultiple = () => setModal({ show: true, type: 'deleteMultiple' });
  const handleMoveMultiple = () => {
    setMoveItem(null);
    setMoveType('multiple');
    setShowFolderTree(true);
  };
  
  const handleDownloadMultiple = async () => {
    const filesToDownload = getSelectedItemsDetails().filter(item => item.type === 'file');
    alert(`${filesToDownload.length} dosya indirilmeye başlanıyor...`);
    for (const file of filesToDownload) {
      try {
        await handleDownloadFile(file);
        await new Promise(resolve => setTimeout(resolve, 300)); 
      } catch (error) {
        console.error(`${file.Adi} indirilirken hata oluştu:`, error);
        alert(`${file.Adi} indirilemedi.`);
      }
    }
  };
  
  const hasFoldersInSelection = () => getSelectedItemsDetails().some(item => item.type === 'folder');

  const handleDownloadFile = async (file) => {
    try {
      const blob = await apiService.downloadFile(ticket.ID, file.Adi, currentPath, file.Adi);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = file.Adi;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      alert('Dosya indirme başarısız: ' + (error.response?.data?.Mesaj || error.message));
    }
  };

  const handleModalAction = async () => {
    const { type, item, itemType } = modal;
    try {
      switch (type) {
        case 'rename':
          if (itemType === 'folder') await apiService.updateFolder(ticket.ID, item.Adi, currentPath, newName);
          else await apiService.updateFile(ticket.ID, item.Adi, currentPath, newName);
          break;
        case 'delete':
          if (itemType === 'folder') await apiService.deleteFolder(ticket.ID, item.Adi, currentPath);
          else await apiService.deleteFile(ticket.ID, item.Adi, currentPath);
          break;
        case 'deleteMultiple':
          const itemsToDelete = getSelectedItemsDetails();
          await Promise.all(itemsToDelete.map(i => {
              if (i.type === 'folder') return apiService.deleteFolder(ticket.ID, i.Adi, currentPath);
              return apiService.deleteFile(ticket.ID, i.Adi, currentPath);
          }));
          break;
        case 'createFolder':
          await apiService.createFolder(ticket.ID, newName, currentPath);
          break;
        case 'createFile':
          await apiService.createFile(ticket.ID, newName, currentPath);
          break;
        default: console.log('Unknown modal action:', type);
      }
      await loadContent();
    } catch (error) {
      alert('İşlem başarısız: ' + (error.response?.data?.Mesaj || error.message));
    } finally {
        setModal({ show: false, type: '', item: null, itemType: null });
        setNewName('');
    }
  };

  const handleMovePathSelect = async (path) => {
    try {
        const itemsToMove = (moveType === 'multiple') ? getSelectedItemsDetails() : [{...moveItem, type: moveType}];
        await Promise.all(itemsToMove.map(item => {
            if (item.type === 'folder') return apiService.moveFolder(ticket.ID, item.Adi, currentPath, path);
            return apiService.moveFile(ticket.ID, item.Adi, currentPath, path);
        }));
        await loadContent();
        alert('Taşıma işlemi başarılı!');
    } catch (error) {
        alert('Taşıma işlemi başarısız: ' + (error.response?.data?.Mesaj || error.message));
    } finally {
        setShowFolderTree(false);
        setMoveItem(null);
        setMoveType('');
    }
  };

  const handleFabClick = (e) => {
    e.stopPropagation();
    setShowCreateMenu(!showCreateMenu);
  };

  const handleFabMenuAction = (action, e) => {
    if (e) e.stopPropagation();
    setShowCreateMenu(false);
    switch (action) {
      case 'upload': setShowUploader(true); break;
      case 'createFile': setModal({ show: true, type: 'createFile' }); setNewName(''); break;
      case 'createFolder': setModal({ show: true, type: 'createFolder' }); setNewName(''); break;
      default: console.log('Unknown FAB action:', action);
    }
  };

  const clearSearch = () => setSearchTerm('');

  const renderBreadcrumb = () => {
    const pathParts = currentPath.split('/').filter(Boolean);
    return (
      <div className="breadcrumb">
        <span className="breadcrumb-item clickable" onClick={() => { setCurrentPath(''); setSearchTerm(''); }}>Anasayfa</span>
        {pathParts.map((part, index) => (
            <React.Fragment key={index}>
              <span className="breadcrumb-separator"> / </span>
              <span className={`breadcrumb-item ${index < pathParts.length - 1 ? 'clickable' : 'current'}`}
                onClick={() => { if (index < pathParts.length - 1) { setCurrentPath(pathParts.slice(0, index + 1).join('/')); setSearchTerm(''); }}}>
                {part}
              </span>
            </React.Fragment>
        ))}
      </div>
    );
  };

  const getModalTitle = (type) => ({ rename: 'Yeniden Adlandır', delete: 'Sil', createFolder: 'Klasör Oluştur', createFile: 'Dosya Oluştur', deleteMultiple: 'Seçilenleri Sil' }[type] || '');
  const getModalButtonText = (type) => ({ rename: 'Yeniden Adlandır', delete: 'Sil', createFolder: 'Oluştur', createFile: 'Oluştur' }[type] || 'Tamam');
  const getMoveItemName = () => moveType === 'multiple' ? `${selectedItems.size} öğe` : moveItem?.Adi || '';

  return (
    <div className="file-explorer">
      <div className="toolbar">
        <div className="toolbar-top">
            {selectedItems.size === 0 ? renderBreadcrumb() : (
                 <div className="selection-toolbar">
                    <div className="toolbar-left-group">
                        <button className="action-button deselect-button" onClick={() => setSelectedItems(new Set())} title="Seçimi Bırak">
                            <XCircle size={20} />
                        </button>
                        <div className="action-buttons">
                            <button className="action-button" onClick={handleMoveMultiple} title="Taşı"><Move size={20} /></button>
                            <button className="action-button" onClick={handleDownloadMultiple} disabled={hasFoldersInSelection()} title="İndir"><Download size={20} /></button>
                            <button className="action-button danger" onClick={handleDeleteMultiple} title="Sil"><Trash2 size={20} /></button>
                        </div>
                    </div>
                    <span className="selection-count">{selectedItems.size} öğe seçildi</span>
                </div>
            )}
        </div>
        <div className="search-container">
          <div className="search-input-wrapper">
            <Search size={20} className="search-icon" />
            <input type="text" placeholder="Dosya veya klasör ara..." value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)} className="search-input" />
            {searchTerm && <button onClick={clearSearch} className="clear-search"><X size={16} /></button>}
          </div>
        </div>
      </div>

      {loading ? (<div className="loading">Yükleniyor...</div>) : (
        <div className="content-grid" onClick={clearSelection}>
          {displayedFolders.map((folder) => (
            <div key={getUniqueId(folder, 'folder')} 
              className={`item folder-item ${selectedItems.has(getUniqueId(folder, 'folder')) ? 'selected' : ''}`}
              onClick={(e) => handleItemClick(e, folder, 'folder')} 
              onDoubleClick={() => handleFolderDoubleClick(folder)}
              onContextMenu={(e) => handleContextMenu(e, folder, 'folder')}>
              <Folder size={48} color="var(--accent-folder)" />
              <span className="item-name">{folder.Adi}</span>
              <button className="more-button" onClick={(e) => { e.stopPropagation(); handleContextMenu(e, folder, 'folder'); }} title="Seçenekler">
                <MoreHorizontal size={20} strokeWidth={2} />
              </button>
            </div>
          ))}
          {displayedFiles.map((file) => (
            <div key={getUniqueId(file, 'file')} 
              className={`item file-item ${selectedItems.has(getUniqueId(file, 'file')) ? 'selected' : ''}`}
              onClick={(e) => handleItemClick(e, file, 'file')} 
              onContextMenu={(e) => handleContextMenu(e, file, 'file')}>
              <File size={48} color="var(--accent-file)" />
              <span className="item-name">{file.Adi}</span>
              <span className="item-size">{file.Boyut} bytes</span>
              <button className="more-button" onClick={(e) => { e.stopPropagation(); handleContextMenu(e, file, 'file'); }} title="Seçenekler">
                <MoreHorizontal size={20} strokeWidth={2} />
              </button>
            </div>
          ))}
          {displayedFolders.length === 0 && displayedFiles.length === 0 && (
            <div className="empty-state">
              <p>{searchTerm ? `"${searchTerm}" için sonuç bulunamadı` : 'Bu klasör boş'}</p>
            </div>
          )}
        </div>
      )}

      {currentPath && <button onClick={handleBackClick} className="back-button-fixed" title="Geri"><ArrowLeft size={24} /></button>}
      
      <div className="top-right-buttons">
        <button onClick={toggleTheme} className="theme-toggle-button" title="Temayı Değiştir">
            {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
        </button>
        <button onClick={logout} className="logout-button-fixed" title="Çıkış Yap"><LogOut size={20} /></button>
      </div>

      <div className="fab-container">
        <button className="fab" onClick={handleFabClick}><Plus size={24} /></button>
        {showCreateMenu && (
          <div className="fab-menu">
            <button onClick={(e) => handleFabMenuAction('upload', e)}><Upload size={20} /> Dosya Yükle</button>
            <button onClick={(e) => handleFabMenuAction('createFile', e)}><FileText size={20} /> Dosya Oluştur</button>
            <button onClick={(e) => handleFabMenuAction('createFolder', e)}><FolderPlus size={20} /> Klasör Oluştur</button>
          </div>
        )}
      </div>

      {contextMenu.show && <ContextMenu {...contextMenu} onAction={handleContextMenuAction} onClose={() => setContextMenu({ show: false })} />}
      {showFolderTree && <FolderTree onSelectPath={handleMovePathSelect} selectedPath={currentPath} itemName={getMoveItemName()} onClose={() => setShowFolderTree(false)} />}
      
      {modal.show && (
        <Modal title={getModalTitle(modal.type)} onClose={() => setModal({ show: false })}>
          {modal.type === 'delete' ? (
            <div>
              <p><strong>{modal.item?.Adi}</strong> silinecek. Emin misiniz?</p>
              <div className="modal-buttons"><button onClick={() => setModal({ show: false })} className="cancel-button">İptal</button><button onClick={handleModalAction} className="danger-button">Sil</button></div>
            </div>
          ) : modal.type === 'deleteMultiple' ? (
             <div>
              <p>Seçili <strong>{selectedItems.size}</strong> öğe silinecek. Bu işlem geri alınamaz. Emin misiniz?</p>
              <div className="modal-buttons"><button onClick={() => setModal({ show: false })} className="cancel-button">İptal</button><button onClick={handleModalAction} className="danger-button">Evet, Sil</button></div>
            </div>
          ) : (
            <div>
              <input type="text" value={newName} onChange={(e) => setNewName(e.target.value)}
                placeholder={modal.type === 'createFolder' ? 'Klasör adı' : 'Dosya adı'}
                onKeyPress={(e) => { if (e.key === 'Enter' && newName.trim()) handleModalAction(); }} autoFocus />
              <div className="modal-buttons"><button onClick={() => setModal({ show: false })} className="cancel-button">İptal</button><button onClick={handleModalAction} disabled={!newName.trim()} className="primary-button">{getModalButtonText(modal.type)}</button></div>
            </div>
          )}
        </Modal>
      )}

      {showUploader && <FileUploader onClose={() => setShowUploader(false)} onUploadComplete={() => { setShowUploader(false); loadContent(); }} />}
    </div>
  );
};

export default FileExplorer;