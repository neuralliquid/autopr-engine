# AutoPR Template Files

This directory contains file generation templates extracted from the AutoPR engine codebase.

## Directory Structure

### `/typescript/`

TypeScript configuration templates:

- `react-tsconfig.json` - React TypeScript configuration
- `vite-tsconfig.json` - Vite TypeScript configuration
- `basic-tsconfig.json` - Basic TypeScript configuration

### `/build/`

Build configuration templates:

- `vite.config.js` - Vite build configuration
- `vitest.config.js` - Vitest testing configuration
- `next.config.js` - Next.js configuration
- `pm2.config.js` - PM2 process manager configuration

### `/docker/`

Docker configuration templates:

- `react.dockerfile` - React application Dockerfile
- `node.dockerfile` - Node.js application Dockerfile
- `generic.dockerfile` - Generic application Dockerfile

### `/testing/`

Testing configuration templates:

- `jest.config.json` - Jest testing configuration
- `vitest.config.json` - Vitest configuration
- `playwright.config.json` - Playwright E2E testing
- `test-setup.js` - Common test setup

### `/security/`

Security configuration templates:

- `helmet.config.json` - Helmet security headers
- `cors.config.json` - CORS configuration
- `env.example` - Environment variables template

### `/deployment/`

Deployment configuration templates:

- `azure-pipeline.yml` - Azure DevOps pipeline
- `github-actions.yml` - GitHub Actions workflow
- `vercel.json` - Vercel deployment config
- `netlify.toml` - Netlify deployment config
- `web.config.xml` - Azure App Service web.config

### `/monitoring/`

Monitoring and maintenance script templates:

- `health-check.sh` - Application health check script
- `monitor.sh` - System monitoring script
- `backup.sh` - Backup script
- `restore.sh` - Restore script

## Usage

These template files are designed to be used by the FileGenerator class and enhancement strategies to generate project-specific configuration files.
