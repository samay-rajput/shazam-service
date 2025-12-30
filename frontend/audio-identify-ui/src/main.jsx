import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

// Global styles reset
const globalStyles = document.createElement("style");
globalStyles.textContent = `
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  
  body {
    margin: 0;
    padding: 0;
    min-height: 100vh;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
  
  button:hover {
    transform: scale(1.02);
  }
  
  button:active {
    transform: scale(0.98);
  }
  
  a:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(29, 185, 84, 0.4);
  }
`;
document.head.appendChild(globalStyles);

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
