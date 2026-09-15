import React from "react";
import ReactDOM from "react-dom/client";
import { HashRouter } from "react-router-dom";
import App from "./App";
import "./styles/globals.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    {/* HashRouter: en una app de escritorio no hay servidor que resuelva rutas */}
    <HashRouter>
      <App />
    </HashRouter>
  </React.StrictMode>,
);
