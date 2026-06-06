# Frontend Setup Guide

## Prerequisites
- Node.js 20.9.0
- Angular CLI 11.1.4

## Installation

1. Install dependencies:
```bash
npm install
```

2. Verify D3.js is installed:
```bash
npm list d3
```

## Running the Development Server

Start the Angular development server:
```bash
npm start
```

The application will be available at `http://localhost:4200`

## Building for Production

Build the application:
```bash
npm run build
```

Output will be in `dist/graph-visualizer/`

## Running Tests

Run unit tests with coverage:
```bash
npm test -- --code-coverage
```

Run tests in headless mode:
```bash
npm test -- --watch=false --browsers=ChromeHeadless
```

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── components/
│   │   │   ├── file-upload.component.ts      # CSV file upload interface
│   │   │   ├── graph-viewer.component.ts     # D3.js graph visualization
│   │   │   ├── detail-panel.component.ts     # Node/relation details display
│   │   │   └── *.spec.ts                     # Component unit tests
│   │   ├── services/
│   │   │   ├── graph.service.ts              # API communication service
│   │   │   └── graph.service.spec.ts         # Service unit tests
│   │   ├── models/
│   │   │   └── graph.model.ts                # TypeScript interfaces
│   │   ├── app.component.ts                  # Main component
│   │   ├── app.module.ts                     # Module configuration
│   │   └── app-routing.module.ts             # Routing configuration
│   ├── index.html                            # Main HTML file
│   ├── main.ts                               # Application entry point
│   ├── polyfills.ts                          # Angular polyfills
│   ├── styles.css                            # Global styles
│   └── test.ts                               # Test environment
├── package.json                              # Dependencies
├── tsconfig.json                             # TypeScript configuration
├── angular.json                              # Angular CLI configuration
├── karma.conf.js                             # Karma test runner config
└── README.md                                 # This file
```

## API Integration

The frontend communicates with the backend API running on `http://localhost:8000`

### API Endpoints Used:
- `POST /api/validate` - Validate CSV files
- `POST /api/load-graph` - Load and parse CSV files

## Features

### File Upload
- Select and upload two CSV files (nodes and relations)
- Validate files before loading
- Display validation errors with detailed messages

### Graph Visualization
- Interactive graph rendering using D3.js
- Pan and zoom functionality
- Click on nodes to view details
- Click on relations to view relationship details

### Detail Panel
- Shows node details: name, UUID, properties
- Shows relation details: type, source, target, UUID, properties
- Real-time property display
- Closeable panel

## Troubleshooting

### Port already in use
If port 4200 is in use:
```bash
ng serve --port 4300
```

### D3.js not loading
Make sure D3.js is properly installed:
```bash
npm install d3@latest
```

### CORS errors from backend
Ensure the backend API is running and CORS is enabled.
Check that `apiUrl` in `graph.service.ts` points to correct backend URL.

### Tests not running
Clear Angular cache:
```bash
ng cache clean
npm test
```

## Environment Configuration

To change API URL, edit `graph.service.ts`:
```typescript
private apiUrl = 'http://localhost:8000/api';
```

For production, update to your production API endpoint.
