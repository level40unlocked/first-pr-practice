import { NavLink, Outlet } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from './LanguageSwitcher';
import './Layout.css';

export default function Layout() {
  const { t } = useTranslation();

  return (
    <div className="app-shell">
      <header className="app-header">
        <NavLink to="/" className="app-logo">
          🏠 {t('appName')}
        </NavLink>
        <nav className="app-nav">
          <NavLink to="/" end>
            {t('nav.listings')}
          </NavLink>
          <NavLink to="/map">{t('nav.map')}</NavLink>
        </nav>
        <LanguageSwitcher />
      </header>
      <main className="app-main">
        <Outlet />
      </main>
      <footer className="app-footer">
        <p>{t('footer.note')}</p>
      </footer>
    </div>
  );
}
