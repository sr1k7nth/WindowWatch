import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Daily from "./components/Daily";
import Weekly from "./components/Weekly";
import Monthly from "./components/Monthly";
import UpdateBanner from "./components/UpdateBanner";
import { useUpdate } from "./hooks/useUpdate";
import "./App.css";

export default function App() {
  const updateInfo = useUpdate();

  return (
    <BrowserRouter>
      <div className="layout">
        <Navbar />

        <main className="app-content">
          {updateInfo && (
            <UpdateBanner version={updateInfo.latest_version} />
          )}

          <Routes>
            <Route path="/" element={<Daily />} />
            <Route path="/daily" element={<Daily />} />
            <Route path="/weekly" element={<Weekly />} />
            <Route path="/monthly" element={<Monthly />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}