import React, { useEffect, useRef } from 'react';
import { Edit, Trash2, Move, Download } from 'lucide-react';
import './ContextMenu.css';

const ContextMenu = ({ x, y, type, onAction, onClose }) => {
  const menuRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        onClose();
      }
    };

    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    const adjustPosition = () => {
      if (menuRef.current) {
        const rect = menuRef.current.getBoundingClientRect();
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;

        let adjustedX = x;
        let adjustedY = y;

        if (x + rect.width > viewportWidth) {
          adjustedX = viewportWidth - rect.width - 10;
        }

        if (y + rect.height > viewportHeight) {
          adjustedY = viewportHeight - rect.height - 10;
        }

        menuRef.current.style.left = `${adjustedX}px`;
        menuRef.current.style.top = `${adjustedY}px`;
      }
    };

    setTimeout(adjustPosition, 0);

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscape);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [x, y, onClose]);

  const handleAction = (action) => {
    onAction(action);
  };

  return (
    <div
      ref={menuRef}
      className="context-menu"
      style={{ left: x, top: y }}
    >
      <button onClick={() => handleAction('rename')}>
        <Edit size={16} />
        Yeniden Adlandır
      </button>
      
      <button onClick={() => handleAction('move')}>
        <Move size={16} />
        Taşı
      </button>
      
      {type === 'file' && (
        <button onClick={() => handleAction('download')}>
          <Download size={16} />
          İndir
        </button>
      )}
      
      <button onClick={() => handleAction('delete')} className="danger">
        <Trash2 size={16} />
        Sil
      </button>
    </div>
  );
};

export default ContextMenu;