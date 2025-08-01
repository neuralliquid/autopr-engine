# AutoPR Configuration Files

This directory contains organized configuration files extracted from the AutoPR engine codebase.

## Directory Structure

### `/platforms/`

Platform-specific configuration files for different development platforms:

- `replit.json` - Replit platform configuration
- `lovable.json` - Lovable.dev platform configuration- `bolt.json` - Bolt.new platform configuration
- `emergent.json` - Emergent.sh platform configuration

### `/packages/`

Package dependency configurations organized by category:

- `security.json` - Security-related packages
- `testing.json` - Testing framework packages
- `performance.json` - Performance optimization packages
- `development.json` - Development tools and utilities
- `monitoring.json` - Monitoring and observability packages

### `/deployment/`

Deployment platform configurations:

- `azure.json` - Azure deployment settings
- `vercel.json` - Vercel deployment settings
- `netlify.json` - Netlify deployment settings
- `railway.json` - Railway deployment settings

### `/workflows/`

Workflow configuration files (moved from autopr/workflows/)

### `/triggers/`

Trigger configuration files (moved from autopr/)

## Usage

These configuration files are designed to be imported and used by the AutoPR engine modules instead
of having hardcoded configurations embedded in Python files.
