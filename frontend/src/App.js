// frontend/src/App.js
import React, { useState } from 'react';
import ChatWindow from './components/ChatWindow';
import { Vortex } from './ui/Vortex';
import './App.css';

function App() {
  const [username, setUsername] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleLogin = (e) => {
    e.preventDefault();
    if (username.trim()) {
      setIsAuthenticated(true);
    }
  };

  return (
    <Vortex backgroundColor="black">
      <div className="App relative z-10 min-h-screen flex flex-col">
        <header className="App-header">
          <h1>SimpleChat</h1>
          <p>Developed by Abhinav Pandey, IIT Kanpur</p>
        </header>
        <main className="flex-1 flex items-center justify-center p-4">
          {!isAuthenticated ? (
            <div className="login-container">
              <h2>Enter Your Username</h2>
              <form onSubmit={handleLogin}>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Your username..."
                  className="username-input"
                />
                <button type="submit" className="login-button">
                  Start Chatting
                </button>
              </form>
            </div>
          ) : (
            <ChatWindow userId={username} />
          )}
        </main>
      </div>
    </Vortex>
  );
}

export default App;