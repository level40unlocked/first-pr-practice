import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import type { Property } from '../data/properties';
import { useLocalizedText } from '../hooks/useLocalizedText';
import './PropertyCard.css';

interface Props {
  property: Property;
}

export default function PropertyCard({ property }: Props) {
  const { t } = useTranslation();
  const localize = useLocalizedText();

  return (
    <Link to={`/listing/${property.id}`} className="property-card">
      <div className="property-card__image" style={{ background: property.imageColor }}>
        <span className="property-card__type">{t(`propertyType.${property.type}`)}</span>
      </div>
      <div className="property-card__body">
        <h3>{localize(property.title)}</h3>
        <p className="property-card__location">
          {localize(property.district)}, {localize(property.city)}
        </p>
        <p className="property-card__price">${property.priceUsd.toLocaleString()}</p>
        <div className="property-card__meta">
          {property.bedrooms > 0 && (
            <span>{t('card.bedrooms', { count: property.bedrooms })}</span>
          )}
          {property.bathrooms > 0 && (
            <span>{t('card.bathrooms', { count: property.bathrooms })}</span>
          )}
          <span>{t('card.area', { area: property.areaSqm })}</span>
        </div>
      </div>
    </Link>
  );
}
