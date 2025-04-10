import React from 'react';

function Inventory({ inventory }) {
  return (
    <div className="Inventory">
      <h2>Your Inventory</h2>
      {inventory.length === 0 ? (
        <p>Your inventory is empty.</p>
      ) : (
        <ul>
          {inventory.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default Inventory;
