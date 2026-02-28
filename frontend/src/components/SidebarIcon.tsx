import { NavLink } from "react-router-dom";

interface SidebarIconProps {
  label: string;
  to: string; 
}

export default function SidebarIcon({ label, to }: SidebarIconProps) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `flex items-center justify-center px-8 py-3 mx-2 rounded-lg text-white font-medium cursor-pointer transition ${
          isActive
            ? "bg-[#030712] "
            : "bg-gray-700 hover:bg-gray-600"
        }`
      }
    >
      {label}
    </NavLink>
  );
}