import type { NextConfig } from "next"
import { withSentryConfig } from "@sentry/nextjs"

const nextConfig: NextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  async rewrites() {
    return [
      {
        source: '/api/ai/:path*',
        destination: 'http://localhost:8000/ai/:path*',
      },
      {
        source: '/ai/:path*',
        destination: 'http://localhost:8000/ai/:path*',
      },
      {
        source: '/api/v1/widgets/:path*',
        destination: 'http://localhost:8000/widgets/:path*',
      },
      {
        source: '/api/v1/:path*',
        destination: 'http://localhost:8000/api/v1/:path*',
      },
      {
        source: '/widgets.json',
        destination: 'http://localhost:8000/widgets.json',
      },
      {
        source: '/templates.json',
        destination: 'http://localhost:8000/templates.json',
      },
    ]
  },
}

const sentryConfig = withSentryConfig(nextConfig, {
  org: "opengodel",
  project: "frontend",
  authToken: process.env.SENTRY_AUTH_TOKEN,
  silent: !process.env.SENTRY_AUTH_TOKEN,
  sourcemaps: {
    disable: true,
  },
  disableLogger: true,
  automaticVercelMonitors: true,
})

export default sentryConfig
