import { useCallback, useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { Sidebar } from "./components/layout/Sidebar";
import { AnalysisPage } from "./pages/AnalysisPage";
import { ResultPage } from "./pages/ResultPage";
import { HistoryPage } from "./pages/HistoryPage";
import { RepositoriesPage } from "./pages/RepositoriesPage";
import { DocumentationPage } from "./pages/DocumentationPage";
import { SettingsPage } from "./pages/SettingsPage";
import { api } from "./services/api";

export default function App() {
  const [activeProfile, setActiveProfile] = useState(null);

  const refreshProfile = useCallback(async () => {
    try {
      const profiles = await api.profiles();
      setActiveProfile(profiles.find((p) => p.is_default) ?? profiles[0] ?? null);
    } catch {
      setActiveProfile(null);
    }
  }, []);

  useEffect(() => {
    refreshProfile();
  }, [refreshProfile]);

  return (
    <div className="shell">
      <Sidebar activeModel={activeProfile?.model} />
      <Routes>
        <Route path="/" element={<AnalysisPage activeProfile={activeProfile} />} />
        <Route path="/analisis/:id" element={<ResultPage />} />
        <Route path="/historial" element={<HistoryPage />} />
        <Route path="/repositorios" element={<RepositoriesPage />} />
        <Route path="/repositorios/documentacion" element={<DocumentationPage />} />
        <Route
          path="/ajustes"
          element={<SettingsPage onProfilesChange={refreshProfile} />}
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}
