import React from 'react';
import { AppProvider, useApp } from './context/AppContext';
import Login from './components/Login';
import FileExplorer from './components/FileExplorer';
import './App.css';

const AppContent = () => {
  const { user, ticket } = useApp();

  if (!user || !ticket) {
    return <Login />;
  }

  return <FileExplorer />;
};

function App() {
  return (
    <AppProvider>
      <div className="App">
        <AppContent />
      </div>
    </AppProvider>
  );
}

export default App;