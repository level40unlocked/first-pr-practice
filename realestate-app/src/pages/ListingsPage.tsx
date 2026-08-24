import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { properties, propertyTypes, type PropertyType } from '../data/properties';
import { useLocalizedText } from '../hooks/useLocalizedText';
import PropertyCard from '../components/PropertyCard';
import './ListingsPage.css';

const EMPTY = '';

export default function ListingsPage() {
  const { t } = useTranslation();
  const localize = useLocalizedText();

  const [city, setCity] = useState(EMPTY);
  const [type, setType] = useState<PropertyType | ''>('');
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');

  const cityOptions = useMemo(() => {
    const seen = new Map<string, string>();
    for (const p of properties) {
      const label = localize(p.city);
      if (!seen.has(label)) seen.set(label, label);
    }
    return Array.from(seen.values());
  }, [localize]);

  const filtered = useMemo(() => {
    return properties.filter((p) => {
      if (city && localize(p.city) !== city) return false;
      if (type && p.type !== type) return false;
      if (minPrice && p.priceUsd < Number(minPrice)) return false;
      if (maxPrice && p.priceUsd > Number(maxPrice)) return false;
      return true;
    });
  }, [city, type, minPrice, maxPrice, localize]);

  const resetFilters = () => {
    setCity(EMPTY);
    setType('');
    setMinPrice('');
    setMaxPrice('');
  };

  return (
    <div>
      <div className="filters">
        <h2>{t('filters.title')}</h2>
        <div className="filters__grid">
          <label>
            {t('filters.city')}
            <select value={city} onChange={(e) => setCity(e.target.value)}>
              <option value="">{t('filters.allCities')}</option>
              {cityOptions.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t('filters.propertyType')}
            <select value={type} onChange={(e) => setType(e.target.value as PropertyType | '')}>
              <option value="">{t('filters.allTypes')}</option>
              {propertyTypes.map((pt) => (
                <option key={pt} value={pt}>
                  {t(`propertyType.${pt}`)}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t('filters.minPrice')}
            <input
              type="number"
              min={0}
              value={minPrice}
              onChange={(e) => setMinPrice(e.target.value)}
              placeholder="0"
            />
          </label>
          <label>
            {t('filters.maxPrice')}
            <input
              type="number"
              min={0}
              value={maxPrice}
              onChange={(e) => setMaxPrice(e.target.value)}
              placeholder="1,000,000"
            />
          </label>
        </div>
        <button type="button" className="filters__reset" onClick={resetFilters}>
          {t('filters.reset')}
        </button>
      </div>

      <p className="results-count">{t('filters.resultsCount', { count: filtered.length })}</p>

      <div className="listing-grid">
        {filtered.map((p) => (
          <PropertyCard key={p.id} property={p} />
        ))}
      </div>
    </div>
  );
}
