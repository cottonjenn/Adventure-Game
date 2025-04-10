import React from 'react';

function GameWindow({ roomDescription, items }) {
  return (
    <div className="GameWindow">
      <h2>Room Description</h2>
      <p>{roomDescription}</p>
      {items.length > 0 && (
        <>
          <h3>Items in the room:</h3>
          <ul>
            {items.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}

export default GameWindow;
