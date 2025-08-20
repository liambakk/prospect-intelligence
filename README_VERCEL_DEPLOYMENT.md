# Vercel Deployment Instructions

## Setup Instructions

### 1. Install Vercel CLI
```bash
npm i -g vercel
```

### 2. Login to Vercel
```bash
vercel login
```

### 3. Set Environment Variables in Vercel Dashboard
Go to your project settings on Vercel and add these environment variables:

- `CLEARBIT_API_KEY` - Your Clearbit API key
- `NEWS_API_KEY` - Your News API key  
- `DATABASE_URL` - Your database connection string
- `BRIGHTDATA_API_KEY` - Your BrightData API key
- `HUNTER_API_KEY` - Your Hunter.io API key
- `OPENAI_API_KEY` - Your OpenAI API key

### 4. Deploy to Vercel

From the `prospect-intelligence` directory:

```bash
vercel
```

For production deployment:
```bash
vercel --prod
```

## Project Structure for Vercel

- `/api/index.py` - Entry point for the Flask application
- `/vercel.json` - Vercel configuration
- `/static/` - Static files (CSS, JS, images)
- `/templates/` - HTML templates
- All Python modules and services

## Notes

- The application uses Flask and is deployed as a Python serverless function
- Static files are served directly from the `/static` directory
- Environment variables are configured through Vercel's dashboard
- Database operations may need adjustment for serverless environment

## Testing Locally with Vercel

```bash
vercel dev
```

This will run the application locally with Vercel's runtime environment.