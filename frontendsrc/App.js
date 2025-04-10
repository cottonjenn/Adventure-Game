import React, { useState, useEffect, useCallback } from 'react';
import GameWindow from './components/GameWindow';
import Inventory from './components/Inventory';
import './styles.css';

function App() {
  const [roomDescription, setRoomDescription] = useState('');
  const [items, setItems] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [health, setHealth] = useState(100);
  const [gameOver, setGameOver] = useState(false);
  const [directions, setDirections] = useState({});

  const fetchGameState = useCallback((endpoint) => {
    fetch(`http://localhost:5000${endpoint}`, { method: 'GET' })
      .then(response => response.json())
      .then(data => {
        console.log(`State from ${endpoint}:`, data);
        setRoomDescription(data.room_description);
        setInventory(data.inventory);
        setHealth(data.health);
        setGameOver(data.game_over);
        setItems(data.items || []);
        setDirections(data.directions || {});
      })
      .catch(error => console.error(`Error fetching ${endpoint}:`, error));
  }, []);

  useEffect(() => {
    fetchGameState('/start');
  }, [fetchGameState]);

  const handleCommand = (command) => {
    if (gameOver) return;
    console.log('Submitting command:', command);
    fetch('http://localhost:5000/command', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command })
    })
      .then(response => {
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        return response.json();
      })
      .then(data => {
        console.log('Response from backend:', data);
        setRoomDescription(data.room_description);
        setInventory(data.inventory);
        setHealth(data.health);
        setGameOver(data.game_over);
        setItems(data.items || []);
        setDirections(data.directions || {});
      })
      .catch(error => console.error('Error processing command:', error));
  };

  const handleReset = () => {
    fetchGameState('/reset');
  };

  return (
    <div className="App">
      <h1>Text Adventure Game</h1>
      <div className="game-container">
        {/* Left Side: Description and Inventory */}
        <div className="left-panel">
          <GameWindow roomDescription={roomDescription} items={items} />
          <Inventory inventory={inventory} />
        </div>
        {/* Right Side: Controls */}
        <div className="right-panel">
          <div className="controls">
            <div className="button-group">
              <h3>Move</h3>
              {Object.entries(directions).map(([dir, dest]) => (
                dest && <button key={dir} onClick={() => handleCommand(`go ${dir}`)}>{`Go ${dir}`}</button>
              ))}
            </div>
            <div className="button-group">
              <h3>Take</h3>
              {items.map(item => (
                <button key={item} onClick={() => handleCommand(`take ${item}`)}>{`Take ${item}`}</button>
              ))}
            </div>
            <div className="button-group">
              <h3>Actions</h3>
              <div className="action-buttons">
                {inventory.map(item => (
                  <>
                    <button key={`use-${item}`} onClick={() => handleCommand(`use ${item}`)}>{`Use ${item}`}</button>
                    <button key={`drop-${item}`} onClick={() => handleCommand(`drop ${item}`)}>{`Drop ${item}`}</button>
                  </>
                ))}
                <button onClick={() => handleCommand('fight')}>Fight</button>
                <button onClick={() => handleCommand('look')}>Look</button>
                <button onClick={() => handleCommand('inventory')}>Inventory</button>
                <button onClick={() => handleCommand('quit')}>Quit</button>
              </div>
            </div>
          </div>
          <p>Health: {health}</p>
          {gameOver && <p className="game-over">Game Over!</p>}
          <button className="reset-btn" onClick={handleReset}>Reset Game</button>
        </div>
      </div>
    </div>
  );
}

export default App;
