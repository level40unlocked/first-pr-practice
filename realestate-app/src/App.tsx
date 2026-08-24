import { Route, Routes } from 'react-router-dom';
import Layout from './components/Layout';
import ListingsPage from './pages/ListingsPage';
import MapPage from './pages/MapPage';
import ListingDetailPage from './pages/ListingDetailPage';

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<ListingsPage />} />
        <Route path="map" element={<MapPage />} />
        <Route path="listing/:id" element={<ListingDetailPage />} />
      </Route>
    </Routes>
  );
}

export default App;
