import React from 'react';
import { useAuth } from './context/AuthContext';
import Login from './components/Login';

function App() {
  const { user, logout } = useAuth();

  if (!user) {
    return <Login />;
  }

  return (
    <div style={{ padding: '20px' }}>
      <h1>Welcome, {user}!</h1>
      <p>You have successfully logged into the Vertica Query Tool.</p>
      <button onClick={logout} style={{ padding: '10px', background: '#dc3545', color: 'white', border: 'none', borderRadius: '5px' }}>
        Logout
      </button>
    </div>
  );
}

export default App;
