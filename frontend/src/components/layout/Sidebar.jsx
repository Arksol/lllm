import { NavLink } from "react-router-dom";

const linkClass = ({ isActive }) =>
  `sidebar__link${isActive ? " sidebar__link--active" : ""}`;

const subClass = ({ isActive }) =>
  `sidebar__sublink${isActive ? " sidebar__sublink--active" : ""}`;

export function Sidebar({ activeModel }) {
  return (
    <nav className="sidebar" aria-label="Navegacion principal">
      <div className="sidebar__logo">LLLM</div>

      <NavLink to="/" className={linkClass} end>
        Nuevo analisis
      </NavLink>
      <NavLink to="/historial" className={linkClass}>
        Historial
      </NavLink>
      <NavLink to="/repositorios" className={linkClass}>
        Repositorios
      </NavLink>
      <NavLink to="/repositorios/documentacion" className={subClass}>
        Documentacion
      </NavLink>
      <NavLink to="/ajustes" className={linkClass}>
        Ajustes
      </NavLink>

      <div className="sidebar__foot">
        Modelo activo
        <strong>{activeModel ?? "sin configurar"}</strong>
      </div>
    </nav>
  );
}
