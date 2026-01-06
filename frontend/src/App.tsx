import { LandingPage } from "./components/LandingPage";
import { LoginPage } from "./pages/LoginPage";
import { DashboardPage } from "./pages/DashboardPage";
import { useAuthStore } from "./store";
import "./styles/App.css";

function App() {
  const { isAuthenticated, currentPage, setPage } = useAuthStore();

  // If authenticated, show dashboard
  if (isAuthenticated) {
    return <DashboardPage />;
  }

  // Otherwise, show landing or login based on currentPage
  if (currentPage === "login") {
    return <LoginPage onBack={() => setPage("landing")} />;
  }

  return <LandingPage onConnectYouTube={() => setPage("login")} />;
}

export default App;
