import type { NextConfig } from "next"

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

export default nextConfig
