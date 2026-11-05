import { useLocation } from "react-router-dom";
import ResidentApp from "../screens/ResidentApp";

// The resident app sits alone inside a phone shape. A new location key on every click of the
// Resident tab remounts it, and it comes back to the same step (see lib/session.js).
export default function Resident() {
  const location = useLocation();
  return (
    <div className="phone-stage">
      <div className="phone">
        <ResidentApp key={location.key} />
      </div>
    </div>
  );
}
