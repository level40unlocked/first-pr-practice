import { CircleMarker, MapContainer, Popup, TileLayer } from 'react-leaflet';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { properties } from '../data/properties';
import { useLocalizedText } from '../hooks/useLocalizedText';
import './MapPage.css';

const VIETNAM_CENTER: [number, number] = [16.0, 106.5];

export default function MapPage() {
  const { t } = useTranslation();
  const localize = useLocalizedText();

  return (
    <div className="map-page">
      <h2>{t('map.title')}</h2>
      <p className="map-page__hint">{t('map.hint')}</p>
      <div className="map-page__container">
        <MapContainer center={VIETNAM_CENTER} zoom={6} scrollWheelZoom style={{ height: '100%', width: '100%' }}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {properties.map((p) => (
            <CircleMarker
              key={p.id}
              center={[p.lat, p.lng]}
              radius={9}
              pathOptions={{ color: '#21867a', fillColor: '#2a9d8f', fillOpacity: 0.9 }}
            >
              <Popup>
                <strong>{localize(p.title)}</strong>
                <br />
                {localize(p.district)}, {localize(p.city)}
                <br />${p.priceUsd.toLocaleString()}
                <br />
                <Link to={`/listing/${p.id}`}>{t('card.viewDetails')}</Link>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>
    </div>
  );
}
