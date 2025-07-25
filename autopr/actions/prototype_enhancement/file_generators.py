"""
File Generation Module

Handles generation of configuration, testing, security, and deployment files for prototype enhancement.
"""

import json
from typing import Dict, List, Any, Optional
from .platform_configs import PlatformRegistry, PlatformConfig


class FileGenerator:
    """Generates various configuration and setup files for different platforms."""
    
    def __init__(self) -> None:
        self.platform_registry = PlatformRegistry()
    
    def generate_dockerfile(self, platform: str) -> str:
        """Generate Dockerfile for the platform."""
        config = self.platform_registry.get_platform_config(platform)
        
        if config.framework == "react":
            return self._generate_react_dockerfile()
        elif config.framework == "express" or config.framework == "node":
            return self._generate_node_dockerfile()
        else:
            return self._generate_generic_dockerfile()
    
    def _generate_react_dockerfile(self) -> str:
        """Generate Dockerfile for React applications."""
        return """
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
        """.strip()
    
    def _generate_node_dockerfile(self) -> str:
        """Generate Dockerfile for Node.js applications."""
        return """
FROM node:18-alpine
WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy application code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodejs -u 1001
USER nodejs

EXPOSE 3000
CMD ["npm", "start"]
        """.strip()
    
    def _generate_generic_dockerfile(self) -> str:
        """Generate generic Dockerfile."""
        return """
FROM node:18-alpine
WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000
CMD ["npm", "start"]
        """.strip()
    
    def generate_typescript_config(self, platform: str) -> str:
        """Generate TypeScript configuration."""
        config = self.platform_registry.get_platform_config(platform)
        
        if config.framework == "react":
            return self._generate_react_tsconfig()
        elif config.name == "bolt":
            return self._generate_vite_tsconfig()
        else:
            return self._generate_basic_tsconfig()
    
    def _generate_react_tsconfig(self) -> str:
        """Generate tsconfig.json for React projects."""
        return json.dumps({
            "compilerOptions": {
                "target": "es5",
                "lib": ["dom", "dom.iterable", "es6"],
                "allowJs": True,
                "skipLibCheck": True,
                "esModuleInterop": True,
                "allowSyntheticDefaultImports": True,
                "strict": True,
                "forceConsistentCasingInFileNames": True,
                "noFallthroughCasesInSwitch": True,
                "module": "esnext",
                "moduleResolution": "node",
                "resolveJsonModule": True,
                "isolatedModules": True,
                "noEmit": True,
                "jsx": "react-jsx"
            },
            "include": ["src"],
            "exclude": ["node_modules"]
        }, indent=2)
    
    def _generate_vite_tsconfig(self) -> str:
        """Generate tsconfig.json for Vite projects."""
        return json.dumps({
            "compilerOptions": {
                "target": "ES2020",
                "useDefineForClassFields": True,
                "lib": ["ES2020", "DOM", "DOM.Iterable"],
                "module": "ESNext",
                "skipLibCheck": True,
                "moduleResolution": "bundler",
                "allowImportingTsExtensions": True,
                "resolveJsonModule": True,
                "isolatedModules": True,
                "noEmit": True,
                "jsx": "react-jsx",
                "strict": True,
                "noUnusedLocals": True,
                "noUnusedParameters": True,
                "noFallthroughCasesInSwitch": True
            },
            "include": ["src"],
            "references": [{"path": "./tsconfig.node.json"}]
        }, indent=2)
    
    def _generate_basic_tsconfig(self) -> str:
        """Generate basic tsconfig.json."""
        return json.dumps({
            "compilerOptions": {
                "target": "es2020",
                "module": "commonjs",
                "lib": ["es2020"],
                "outDir": "./dist",
                "rootDir": "./src",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True,
                "resolveJsonModule": True
            },
            "include": ["src/**/*"],
            "exclude": ["node_modules", "dist"]
        }, indent=2)
    
    def generate_next_config(self, platform: str) -> str:
        """Generate Next.js configuration."""
        return """
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    appDir: true,
  },
  images: {
    domains: ['localhost'],
  },
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
}

module.exports = nextConfig
        """.strip()
    
    def generate_testing_files(self, platform: str) -> Dict[str, str]:
        """Generate testing configuration files."""
        config = self.platform_registry.get_platform_config(platform)
        files: Dict[str, str] = {}
        
        if config.framework == "react":
            files.update(self._generate_react_testing_files())
        
        files.update(self._generate_common_testing_files())
        return files
    
    def _generate_react_testing_files(self) -> Dict[str, str]:
        """Generate React testing setup."""
        return {
            "src/setupTests.ts": """
import '@testing-library/jest-dom';
            """.strip(),
            
            "src/__tests__/App.test.tsx": """
import { render, screen } from '@testing-library/react';
import App from '../App';

test('renders learn react link', () => {
  render(<App />);
  const linkElement = screen.getByText(/learn react/i);
  expect(linkElement).toBeInTheDocument();
});
            """.strip(),
            
            "jest.config.js": """
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
  moduleNameMapping: {
    '\\\\.(css|less|scss|sass)$': 'identity-obj-proxy',
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/index.tsx',
    '!src/reportWebVitals.ts',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};
            """.strip()
        }
    
    def _generate_common_testing_files(self) -> Dict[str, str]:
        """Generate common testing files."""
        return {
            ".github/workflows/test.yml": """
name: Test
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      - name: Install dependencies
        run: npm ci
      - name: Run tests
        run: npm test -- --coverage --watchAll=false
      - name: Upload coverage
        uses: codecov/codecov-action@v3
            """.strip(),
            
            "playwright.config.ts": """
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
  ],
  webServer: {
    command: 'npm start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
            """.strip()
        }
    
    def generate_security_files(self, platform: str) -> Dict[str, str]:
        """Generate security configuration files."""
        config = self.platform_registry.get_platform_config(platform)
        files: Dict[str, str] = {}
        
        files[".env.example"] = self._generate_env_example(config)
        files["security/helmet.config.js"] = self._generate_helmet_config()
        files["security/cors.config.js"] = self._generate_cors_config()
        
        if config.framework == "react":
            files["public/.htaccess"] = self._generate_htaccess()
        
        return files
    
    def _generate_env_example(self, config: PlatformConfig) -> str:
        """Generate environment variables example."""
        env_vars = [
            "# Environment Configuration",
            "NODE_ENV=development",
            "PORT=3000",
            "",
            "# Database",
            "DATABASE_URL=postgresql://user:password@localhost:5432/dbname",
            "",
            "# Authentication",
            "JWT_SECRET=your-secret-key-here",
            "SESSION_SECRET=your-session-secret",
            "",
            "# External APIs",
            "API_KEY=your-api-key",
            "",
            "# Monitoring",
            "SENTRY_DSN=your-sentry-dsn",
            "",
            "# Feature Flags",
            "ENABLE_FEATURE_X=false"
        ]
        
        if config.framework == "react":
            env_vars.extend([
                "",
                "# React App Variables (must start with REACT_APP_)",
                "REACT_APP_API_URL=http://localhost:3001",
                "REACT_APP_ENVIRONMENT=development"
            ])
        
        return "\n".join(env_vars)
    
    def _generate_helmet_config(self) -> str:
        """Generate Helmet security configuration."""
        return """
const helmet = require('helmet');

const helmetConfig = {
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
      fontSrc: ["'self'", "https://fonts.gstatic.com"],
      imgSrc: ["'self'", "data:", "https:"],
      scriptSrc: ["'self'"],
      connectSrc: ["'self'"],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true,
  },
};

module.exports = helmetConfig;
        """.strip()
    
    def _generate_cors_config(self) -> str:
        """Generate CORS configuration."""
        return """
const corsConfig = {
  origin: process.env.NODE_ENV === 'production' 
    ? ['https://yourdomain.com'] 
    : ['http://localhost:3000', 'http://localhost:3001'],
  credentials: true,
  optionsSuccessStatus: 200,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
};

module.exports = corsConfig;
        """.strip()
    
    def _generate_htaccess(self) -> str:
        """Generate .htaccess for React apps."""
        return """
Options -MultiViews
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule ^ index.html [QSA,L]

# Security headers
Header always set X-Content-Type-Options nosniff
Header always set X-Frame-Options DENY
Header always set X-XSS-Protection "1; mode=block"
Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
        """.strip()
    
    def generate_storybook_config(self) -> Dict[str, str]:
        """Generate Storybook configuration."""
        return {
            ".storybook/main.js": """
module.exports = {
  stories: ['../src/**/*.stories.@(js|jsx|ts|tsx)'],
  addons: [
    '@storybook/addon-essentials',
    '@storybook/addon-interactions',
    '@storybook/addon-a11y',
  ],
  framework: {
    name: '@storybook/react-webpack5',
    options: {},
  },
  docs: {
    autodocs: 'tag',
  },
};
            """.strip(),
            
            ".storybook/preview.js": """
export const parameters = {
  actions: { argTypesRegex: '^on[A-Z].*' },
  controls: {
    matchers: {
      color: /(background|color)$/i,
      date: /Date$/,
    },
  },
};
            """.strip(),
            
            "src/components/Button/Button.stories.tsx": """
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta: Meta<typeof Button> = {
  title: 'Example/Button',
  component: Button,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    backgroundColor: { control: 'color' },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Primary: Story = {
  args: {
    primary: true,
    label: 'Button',
  },
};

export const Secondary: Story = {
  args: {
    label: 'Button',
  },
};
            """.strip()
        }
    
    def generate_accessibility_testing(self) -> Dict[str, str]:
        """Generate accessibility testing setup."""
        return {
            "src/utils/axe-config.ts": """
import { configureAxe } from 'jest-axe';

const axe = configureAxe({
  rules: {
    // Disable color-contrast rule for now
    'color-contrast': { enabled: false },
  },
});

export default axe;
            """.strip(),
            
            "src/__tests__/accessibility.test.tsx": """
import { render } from '@testing-library/react';
import axe from '../utils/axe-config';
import App from '../App';

describe('Accessibility tests', () => {
  test('should not have any accessibility violations', async () => {
    const { container } = render(<App />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
            """.strip()
        }
    
    def generate_azure_configs(self, platform: str) -> Dict[str, str]:
        """Generate Azure-specific configuration files."""
        config = self.platform_registry.get_platform_config(platform)
        files: Dict[str, str] = {}
        
        # Azure App Service configuration
        files["azure-pipelines.yml"] = self._generate_azure_pipeline(config)
        files["web.config"] = self._generate_web_config(config)
        
        if config.framework == "react":
            files["staticwebapp.config.json"] = self._generate_static_web_app_config()
        
        return files
    
    def _generate_azure_pipeline(self, config: PlatformConfig) -> str:
        """Generate Azure DevOps pipeline."""
        return f"""
trigger:
- main

pool:
  vmImage: 'ubuntu-latest'

variables:
  nodeVersion: '18.x'

stages:
- stage: Build
  displayName: 'Build stage'
  jobs:
  - job: Build
    displayName: 'Build job'
    steps:
    - task: NodeTool@0
      inputs:
        versionSpec: '$(nodeVersion)'
      displayName: 'Install Node.js'
    
    - script: |
        npm ci
      displayName: 'Install dependencies'
    
    - script: |
        npm run test -- --coverage --watchAll=false
      displayName: 'Run tests'
    
    - script: |
        {config.build_command}
      displayName: 'Build application'
    
    - task: ArchiveFiles@2
      inputs:
        rootFolderOrFile: '$(System.DefaultWorkingDirectory)'
        includeRootFolder: false
        archiveType: 'zip'
        archiveFile: '$(Build.ArtifactStagingDirectory)/$(Build.BuildId).zip'
        replaceExistingArchive: true
    
    - task: PublishBuildArtifacts@1
      inputs:
        PathtoPublish: '$(Build.ArtifactStagingDirectory)'
        ArtifactName: 'drop'
        publishLocation: 'Container'
        """.strip()
    
    def _generate_web_config(self, config: PlatformConfig) -> str:
        """Generate web.config for Azure App Service."""
        if config.framework == "react":
            return """
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="React Routes" stopProcessing="true">
          <match url=".*" />
          <conditions logicalGrouping="MatchAll">
            <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
            <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
          </conditions>
          <action type="Rewrite" url="/" />
        </rule>
      </rules>
    </rewrite>
    <httpHeaders>
      <add name="X-Content-Type-Options" value="nosniff" />
      <add name="X-Frame-Options" value="DENY" />
      <add name="X-XSS-Protection" value="1; mode=block" />
    </httpHeaders>
  </system.webServer>
</configuration>
            """.strip()
        else:
            return """
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="iisnode" path="index.js" verb="*" modules="iisnode"/>
    </handlers>
    <rewrite>
      <rules>
        <rule name="DynamicContent">
          <match url="/*" />
          <action type="Rewrite" url="index.js"/>
        </rule>
      </rules>
    </rewrite>
    <httpHeaders>
      <add name="X-Content-Type-Options" value="nosniff" />
      <add name="X-Frame-Options" value="DENY" />
      <add name="X-XSS-Protection" value="1; mode=block" />
    </httpHeaders>
  </system.webServer>
</configuration>
            """.strip()
    
    def _generate_static_web_app_config(self) -> str:
        """Generate Azure Static Web Apps configuration."""
        return json.dumps({
            "routes": [
                {
                    "route": "/api/*",
                    "allowedRoles": ["authenticated"]
                },
                {
                    "route": "/*",
                    "serve": "/index.html",
                    "statusCode": 200
                }
            ],
            "responseOverrides": {
                "401": {
                    "redirect": "/login",
                    "statusCode": 302
                }
            },
            "globalHeaders": {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block"
            }
        }, indent=2)
    
    def generate_deployment_automation(self, platform: str) -> Dict[str, str]:
        """Generate deployment automation scripts."""
        config = self.platform_registry.get_platform_config(platform)
        files: Dict[str, str] = {}
        
        # GitHub Actions workflow
        files[".github/workflows/deploy.yml"] = self._generate_github_actions_deploy(config)
        
        # Platform-specific deployment configs
        for target in config.deployment_targets:
            if target == "vercel":
                files["vercel.json"] = self._generate_vercel_config(config)
            elif target == "netlify":
                files["netlify.toml"] = self._generate_netlify_config(config)
        
        return files
    
    def _generate_github_actions_deploy(self, config: PlatformConfig) -> str:
        """Generate GitHub Actions deployment workflow."""
        return f"""
name: Deploy
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      - name: Install dependencies
        run: npm ci
      - name: Run tests
        run: npm test -- --coverage --watchAll=false
      - name: Build
        run: {config.build_command}

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      - name: Install dependencies
        run: npm ci
      - name: Build
        run: {config.build_command}
      - name: Deploy
        run: echo "Add deployment step here"
        """.strip()
    
    def _generate_vercel_config(self, config: PlatformConfig) -> str:
        """Generate Vercel configuration."""
        vercel_config = {
            "version": 2,
            "builds": [
                {
                    "src": "package.json",
                    "use": "@vercel/node" if config.framework in ["express", "node"] else "@vercel/static-build"
                }
            ]
        }
        
        if config.framework == "react":
            vercel_config["routes"] = [
                {"handle": "filesystem"},
                {"src": "/.*", "dest": "/index.html"}
            ]
        
        return json.dumps(vercel_config, indent=2)
    
    def _generate_netlify_config(self, config: PlatformConfig) -> str:
        """Generate Netlify configuration."""
        return f"""
[build]
  publish = "build"
  command = "{config.build_command}"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
        """.strip()
    
    def generate_monitoring_scripts(self, platform: str) -> Dict[str, str]:
        """Generate monitoring scripts."""
        return {
            "scripts/health_check.sh": """
#!/bin/bash
# Health check script
set -e

echo "Checking application health..."

# Check if the application is responding
if curl -f http://localhost:3000/health > /dev/null 2>&1; then
    echo "✅ Application is healthy"
    exit 0
else
    echo "❌ Application health check failed"
    exit 1
fi
            """.strip(),
            
            "scripts/monitor.sh": """
#!/bin/bash
# Monitoring script
set -e

echo "Starting application monitoring..."

# Monitor CPU and memory usage
while true; do
    echo "$(date): CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%, Memory: $(free | grep Mem | awk '{printf("%.2f%%", $3/$2 * 100.0)}')"
    sleep 30
done
            """.strip(),
            
            "scripts/alert_on_failure.sh": """
#!/bin/bash
# Alert script for failures
set -e

SERVICE_NAME="$1"
ERROR_MESSAGE="$2"

echo "ALERT: $SERVICE_NAME failed - $ERROR_MESSAGE"

# Add your alerting logic here
# Examples:
# - Send email
# - Post to Slack
# - Send to monitoring service
# - Log to external system

# Example webhook notification
# curl -X POST -H 'Content-type: application/json' \\
#   --data '{"text":"ALERT: '$SERVICE_NAME' failed - '$ERROR_MESSAGE'"}' \\
#   $SLACK_WEBHOOK_URL
            """.strip()
        }
    
    def generate_backup_scripts(self, platform: str) -> Dict[str, str]:
        """Generate backup scripts."""
        return {
            "scripts/backup.sh": """
#!/bin/bash
# Backup script
set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "Creating backup at $TIMESTAMP..."

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database (if applicable)
if [ ! -z "$DATABASE_URL" ]; then
    echo "Backing up database..."
    pg_dump $DATABASE_URL > $BACKUP_DIR/db_backup_$TIMESTAMP.sql
fi

# Backup uploaded files (if applicable)
if [ -d "./uploads" ]; then
    echo "Backing up uploaded files..."
    tar -czf $BACKUP_DIR/uploads_backup_$TIMESTAMP.tar.gz ./uploads
fi

# Backup configuration
echo "Backing up configuration..."
cp .env $BACKUP_DIR/env_backup_$TIMESTAMP

echo "✅ Backup completed: $BACKUP_DIR"
            """.strip(),
            
            "scripts/restore.sh": """
#!/bin/bash
# Restore script
set -e

BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

echo "Restoring from backup: $BACKUP_FILE"

# Restore database
if [[ $BACKUP_FILE == *.sql ]]; then
    echo "Restoring database..."
    psql $DATABASE_URL < $BACKUP_FILE
fi

# Restore files
if [[ $BACKUP_FILE == *.tar.gz ]]; then
    echo "Restoring files..."
    tar -xzf $BACKUP_FILE
fi

echo "✅ Restore completed"
            """.strip()
        }
