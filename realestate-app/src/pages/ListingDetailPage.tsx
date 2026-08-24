import { Link, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { MapContainer, TileLayer, CircleMarker } from 'react-leaflet';
import { properties } from '../data/properties';
import { useLocalizedText } from '../hooks/useLocalizedText';
import './ListingDetailPage.css';

export default function ListingDetailPage() {
  const { id } = useParams();
  const { t } = useTranslation();
  const localize = useLocalizedText();
  const property = properties.find((p) => p.id === id);

  if (!property) {
    return (
      <div className="detail-page">
        <p>{t('detail.notFound')}</p>
        <Link to="/">{t('detail.back')}</Link>
      </div>
    );
  }

  return (
    <div className="detail-page">
      <Link to="/" className="detail-page__back">
        &larr; {t('detail.back')}
      </Link>

      <div className="detail-page__hero" style={{ background: property.imageColor }}>
        <span className="detail-page__type">{t(`propertyType.${property.type}`)}</span>
      </div>

      <h1>{localize(property.title)}</h1>
      <p className="detail-page__location">
        {localize(property.district)}, {localize(property.city)}
      </p>
      <p className="detail-page__price">${property.priceUsd.toLocaleString()}</p>

      <div className="detail-page__stats">
        <div>
          <span className="label">{t('detail.area')}</span>
          <span className="value">{property.areaSqm} m²</span>
        </div>
        {property.bedrooms > 0 && (
          <div>
            <span className="label">{t('detail.bedrooms')}</span>
            <span className="value">{property.bedrooms}</span>
          </div>
        )}
        {property.bathrooms > 0 && (
          <div>
            <span className="label">{t('detail.bathrooms')}</span>
            <span className="value">{property.bathrooms}</span>
          </div>
        )}
      </div>

      <section>
        <h2>{t('detail.overview')}</h2>
        <p>{localize(property.description)}</p>
      </section>

      <section>
        <h2>{t('detail.location')}</h2>
        <div className="detail-page__map">
          <MapContainer
            center={[property.lat, property.lng]}
            zoom={14}
            scrollWheelZoom={false}
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <CircleMarker
              center={[property.lat, property.lng]}
              radius={10}
              pathOptions={{ color: '#21867a', fillColor: '#2a9d8f', fillOpacity: 0.9 }}
            />
          </MapContainer>
        </div>
      </section>

      <section>
        <h2>{t('detail.contact')}</h2>
        <p>{property.contactName}</p>
        <a className="detail-page__call" href={`tel:${property.contactPhone.replace(/\s+/g, '')}`}>
          {t('detail.call')}: {property.contactPhone}
        </a>
      </section>
    </div>
  );
}
