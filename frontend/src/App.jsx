import { NavLink, Navigate, Route, Routes, useLocation } from "react-router-dom";
import Demo from "./pages/Demo";
import Review from "./pages/Review";
import Resident from "./pages/Resident";
import Staff from "./pages/Staff";

const links = [
  { to: "/resident", label: "Resident" },
  { to: "/staff", label: "Staff" },
  { to: "/demo", label: "Demo" },
  { to: "/review", label: "Review AI steps" },
];

export default function App() {
  // The resident app is a phone prototype on its own: no team tabs around it.
  const onResident = useLocation().pathname.startsWith("/resident");
  return (
    <>
      {!onResident && <nav className="topnav" aria-label="Main">
        <strong className="brand">Carryover</strong>
        {links.map((l) => (
          <NavLink key={l.to} to={l.to} className={({ isActive }) => (isActive ? "active" : "")}>
            {l.label}
          </NavLink>
        ))}
      </nav>}
      <main className={onResident ? "" : "page"}>
        <Routes>
          <Route path="/" element={<Navigate to="/demo" replace />} />
          <Route path="/resident" element={<Resident />} />
          <Route path="/staff" element={<Staff />} />
          <Route path="/demo" element={<Demo />} />
          <Route path="/review" element={<Review />} />
        </Routes>
      </main>
    </>
  );
}
