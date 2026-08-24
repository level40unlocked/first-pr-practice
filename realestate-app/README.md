# VietHome — Vietnam Real Estate App

A web app for browsing real estate listings in Vietnam, built with React, TypeScript, and Vite.

## Features

- **Listings & search** — filter properties by city, property type, and price range.
- **Map-based search** — browse listings on an interactive map (Leaflet + OpenStreetMap, no API key required).
- **Listing details** — photos placeholder, price, area, bedrooms/bathrooms, description, location map, and contact info.
- **Multilingual UI** — Vietnamese, Korean, and English, switchable at any time (choice is remembered in the browser).

All property data is mock/demo data for practice purposes — not real listings.

## Tech stack

- React 19 + TypeScript
- Vite
- React Router
- react-i18next (i18n)
- Leaflet / react-leaflet (maps)

## Getting started

```bash
cd realestate-app
npm install
npm run dev
```

Then open the printed local URL in your browser.

## Scripts

- `npm run dev` — start the dev server
- `npm run build` — type-check and build for production
- `npm run preview` — preview the production build locally
- `npm run lint` — run oxlint

## Project structure

```
src/
  components/   Layout, PropertyCard, LanguageSwitcher
  pages/        ListingsPage, MapPage, ListingDetailPage
  data/         mock property dataset
  i18n/         translation resources (vi/ko/en) and i18next setup
  hooks/        useLocalizedText helper for picking the right language field
```

## Next steps / ideas

- Replace mock data with a real backend/API.
- Add authentication for agents to post listings.
- Add photo uploads instead of placeholder colors.
- Add saved searches / favorites.
