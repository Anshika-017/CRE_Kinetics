# Reaction Kinetics — Frontend

React + TypeScript + Vite single-page app. Renders equations with KaTeX,
charts with Plotly, and talks to the backend via `VITE_API_BASE_URL`.

## Setup

```bash
npm install
cp .env.example .env   # edit VITE_API_BASE_URL if needed
```

## Run (dev)

```bash
npm run dev
```

## Build

```bash
npm run build   # outputs to dist/
npm run preview # serve the production build locally
```

## Deployment (Render — Static Site)

- Root directory: `frontend`
- Build command: `npm install && npm run build`
- Publish directory: `dist`
- Environment variable: `VITE_API_BASE_URL=https://your-backend.onrender.com`
