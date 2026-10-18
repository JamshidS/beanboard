import { Link, Route, Routes } from "react-router-dom";
import BeansPage from "./pages/BeansPage";
import BeanDetailPage from "./pages/BeanDetailPage";

export default function App() {
  return (
    <>
      <header className="site-header">
        <div className="container">
          <Link to="/" className="brand">
            <span className="brand-mark">&#9749;</span> Beanboard
          </Link>
          <span className="tagline">Specialty coffee, honestly reviewed</span>
        </div>
      </header>
      <main className="container">
        <Routes>
          <Route path="/" element={<BeansPage />} />
          <Route path="/beans/:beanId" element={<BeanDetailPage />} />
          <Route path="*" element={<p className="status">Page not found.</p>} />
        </Routes>
      </main>
    </>
  );
}
