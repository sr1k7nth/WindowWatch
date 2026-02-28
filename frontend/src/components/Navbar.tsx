import { NavLink } from "react-router-dom";
import { ChartSpline } from "lucide-react";
import "../css/Navbar.css";
import githubLogo from "../assets/GitHub_Invertocat_White_Clearspace.svg";

export default function Navbar() {
  return (
    <div className="nav-wrapper">
      <div className="navbar">
        <div className="nav-left">
          <ChartSpline />
          <span className="logo-text">Screen Time</span>
        </div>

        <div className="nav-center">
          <NavLink to="/" className="pill">
            Daily
          </NavLink>
          <NavLink to="/weekly" className="pill">
            Weekly
          </NavLink>
          <NavLink to="/monthly" className="pill">
            Monthly
          </NavLink>
        </div>

        <div className="nav-right">
          <a href="https://github.com/sr1k7nth/WinTrack" target="_blank" rel="noopener noreferrer">
            <img
              src={githubLogo}
              className="w-12 h-12 hover:w-14 hover:h-14 hover:shadow- transition-all duration-300"
              alt="github"
            />
          </a>
        </div>
      </div>
    </div>
  );
}
