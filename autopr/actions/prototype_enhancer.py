"""
AutoPR Action: Prototype Enhancer
Enhances prototypes based on detected platform for production readiness
"""

import json
import os
from typing import Dict, List, Any, Optional, Callable
from pydantic import BaseModel, Field
from datetime import datetime


class PrototypeEnhancerInputs(BaseModel):
    platform: str
    project_files: Dict[str, str] = Field(default_factory=dict)
    enhancement_type: str = (
        "production_ready"  # "production_ready", "testing", "security", "performance"
    )
    target_environment: str = "production"
    workspace_path: str = "."


class PrototypeEnhancerOutputs(BaseModel):
    enhanced_files: Dict[str, str]
    new_files: Dict[str, str]
    enhancement_summary: str
    production_checklist: List[str]
    deployment_config: Dict[str, Any]
    estimated_effort: str
    next_steps: List[str]


class PrototypeEnhancer:
    def __init__(self) -> None:
        self.enhancement_strategies: Dict[
            str, Callable[[PrototypeEnhancerInputs], PrototypeEnhancerOutputs]
        ] = {
            "replit": self._enhance_replit_project,
            "lovable": self._enhance_lovable_project,
            "bolt": self._enhance_bolt_project,
            "same": self._enhance_same_project,
            "emergent": self._enhance_emergent_project,
        }

        # Common production enhancements
        self.common_enhancements: Dict[str, List[str]] = {
            "security": [
                "helmet",
                "cors",
                "express-rate-limit",
                "bcryptjs",
                "jsonwebtoken",
                "express-validator",
            ],
            "performance": ["compression", "morgan", "cluster", "pm2"],
            "monitoring": [
                "@azure/monitor-opentelemetry-exporter",
                "winston",
                "express-prometheus-middleware",
            ],
            "testing": [
                "jest",
                "@testing-library/react",
                "@testing-library/jest-dom",
                "playwright",
                "supertest",
            ],
        }

    def enhance_prototype(
        self, inputs: PrototypeEnhancerInputs
    ) -> PrototypeEnhancerOutputs:
        """Enhance prototype for production readiness"""

        if inputs.platform in self.enhancement_strategies:
            return self.enhancement_strategies[inputs.platform](inputs)
        else:
            return self._generic_enhancement(inputs)

    def _enhance_replit_project(
        self, inputs: PrototypeEnhancerInputs
    ) -> PrototypeEnhancerOutputs:
        """Enhance Replit-generated project"""

        enhanced_files: Dict[str, str] = {}
        new_files: Dict[str, str] = {}

        # Enhance package.json for production
        if "package.json" in inputs.project_files:
            package_json: Dict = json.loads(inputs.project_files["package.json"])
            enhanced_package: Dict = self._enhance_package_json_for_replit(package_json)
            enhanced_files["package.json"] = json.dumps(enhanced_package, indent=2)

        # Add production configuration files
        new_files.update(self._generate_replit_production_files(inputs))

        # Add Azure-specific configurations
        new_files.update(self._generate_azure_configs("replit"))

        # Add testing and security configuration
        if inputs.enhancement_type == "production_ready":
            new_files.update(self._generate_testing_files("replit"))
            new_files.update(self._generate_security_files("replit"))
        elif inputs.enhancement_type == "testing":
            new_files.update(self._generate_testing_files("replit"))
        elif inputs.enhancement_type == "security":
            new_files.update(self._generate_security_files("replit"))

        production_checklist: List[str] = self._get_production_checklist("replit")
        deployment_config: Dict[str, Any] = self._get_deployment_config("replit")

        return PrototypeEnhancerOutputs(
            enhanced_files=enhanced_files,
            new_files=new_files,
            enhancement_summary=f"Enhanced Replit project for {inputs.target_environment} deployment with security, testing, and monitoring",
            production_checklist=production_checklist,
            deployment_config=deployment_config,
            estimated_effort="2-4 hours manual work → 15 minutes automated",
            next_steps=self._get_next_steps("replit", inputs.enhancement_type),
        )

    def _enhance_lovable_project(
        self, inputs: PrototypeEnhancerInputs
    ) -> PrototypeEnhancerOutputs:
        """Enhance Lovable.dev project"""

        enhanced_files: Dict[str, str] = {}
        new_files: Dict[str, str] = {}

        # Enhance for React/TypeScript best practices
        if "package.json" in inputs.project_files:
            package_json: Dict = json.loads(inputs.project_files["package.json"])
            enhanced_package: Dict = self._enhance_package_json_for_lovable(
                package_json
            )
            enhanced_files["package.json"] = json.dumps(enhanced_package, indent=2)

        # Add TypeScript configurations
        new_files["tsconfig.json"] = self._generate_typescript_config("lovable")
        new_files["next.config.js"] = self._generate_next_config("lovable")

        # Add component testing setup
        new_files.update(self._generate_react_testing_setup())

        # Add Storybook configuration
        new_files.update(self._generate_storybook_config())

        # Add accessibility testing
        new_files.update(self._generate_accessibility_testing())

        return PrototypeEnhancerOutputs(
            enhanced_files=enhanced_files,
            new_files=new_files,
            enhancement_summary="Enhanced Lovable.dev project with TypeScript, testing, Storybook, and accessibility features",
            production_checklist=self._get_production_checklist("lovable"),
            deployment_config=self._get_deployment_config("lovable"),
            estimated_effort="3-6 hours manual work → 20 minutes automated",
            next_steps=self._get_next_steps("lovable", inputs.enhancement_type),
        )

    def _enhance_bolt_project(
        self, inputs: PrototypeEnhancerInputs
    ) -> PrototypeEnhancerOutputs:
        """Enhance Bolt.new full-stack project"""

        enhanced_files: Dict[str, str] = {}
        new_files: Dict[str, str] = {}

        # Add database management
        new_files.update(self._generate_database_management("bolt"))

        # Add API documentation
        new_files.update(self._generate_api_documentation("bolt"))

        # Add full-stack testing
        new_files.update(self._generate_fullstack_testing("bolt"))

        # Add monitoring and logging
        new_files.update(self._generate_monitoring_config("bolt"))

        # Add Docker configurations
        new_files.update(self._generate_docker_compose("bolt"))
        new_files.update({"Dockerfile": self._generate_dockerfile("bolt")})

        production_checklist: List[str] = self._get_production_checklist("bolt")
        deployment_config: Dict[str, Any] = self._get_deployment_config("bolt")

        return PrototypeEnhancerOutputs(
            enhanced_files=enhanced_files,
            new_files=new_files,
            enhancement_summary="Bolt.new project enhanced for full-stack production readiness",
            production_checklist=production_checklist,
            deployment_config=deployment_config,
            estimated_effort="2-4 hours manual work → 15 minutes automated",
            next_steps=self._get_next_steps("bolt", inputs.enhancement_type),
        )

    def _enhance_same_project(
        self, inputs: PrototypeEnhancerInputs
    ) -> PrototypeEnhancerOutputs:
        """Enhance Same.new cloned project"""

        enhanced_files: Dict[str, str] = {}
        new_files: Dict[str, str] = {}

        # Add customization framework
        new_files.update(self._generate_customization_framework("same"))

        # Add branding system
        new_files.update(self._generate_branding_system("same"))

        # Add feature toggle system
        new_files.update(self._generate_feature_toggles("same"))

        return PrototypeEnhancerOutputs(
            enhanced_files=enhanced_files,
            new_files=new_files,
            enhancement_summary="Enhanced Same.new project with customization framework and feature management",
            production_checklist=self._get_production_checklist("same"),
            deployment_config=self._get_deployment_config("same"),
            estimated_effort="2-4 hours manual work → 20 minutes automated",
            next_steps=self._get_next_steps("same", inputs.enhancement_type),
        )

    def _enhance_emergent_project(
        self, inputs: PrototypeEnhancerInputs
    ) -> PrototypeEnhancerOutputs:
        """Enhance Emergent.sh automation project"""

        enhanced_files: Dict[str, str] = {}
        new_files: Dict[str, str] = {}

        # Add advanced deployment scripts
        new_files.update(self._generate_deployment_automation("emergent"))

        # Add monitoring scripts
        new_files.update(self._generate_monitoring_scripts("emergent"))

        # Add backup and recovery
        new_files.update(self._generate_backup_scripts("emergent"))

        return PrototypeEnhancerOutputs(
            enhanced_files=enhanced_files,
            new_files=new_files,
            enhancement_summary="Enhanced Emergent.sh project with advanced DevOps automation",
            production_checklist=self._get_production_checklist("emergent"),
            deployment_config=self._get_deployment_config("emergent"),
            estimated_effort="3-6 hours manual work → 30 minutes automated",
            next_steps=self._get_next_steps("emergent", inputs.enhancement_type),
        )

    def _enhance_package_json_for_replit(self, package_json: Dict) -> Dict:
        """Enhance package.json for Replit projects"""

        # Ensure required scripts exist
        scripts: Dict = package_json.setdefault("scripts", {})
        scripts.update(
            {
                "start": "node index.js",
                "dev": "nodemon index.js",
                "build": 'echo "Build step for production"',
                "test": "jest",
                "test:watch": "jest --watch",
                "lint": "eslint .",
                "lint:fix": "eslint . --fix",
            }
        )

        # Add production dependencies
        deps: Dict = package_json.setdefault("dependencies", {})
        deps.update(
            {
                "helmet": "^7.0.0",
                "cors": "^2.8.5",
                "compression": "^1.7.4",
                "dotenv": "^16.0.0",
                "express-rate-limit": "^6.7.0",
            }
        )

        # Add development dependencies
        dev_deps: Dict = package_json.setdefault("devDependencies", {})
        dev_deps.update(
            {
                "nodemon": "^2.0.22",
                "jest": "^29.5.0",
                "eslint": "^8.42.0",
                "prettier": "^2.8.8",
            }
        )

        # Add engines specification
        package_json["engines"] = {"node": ">=18.0.0", "npm": ">=8.0.0"}

        return package_json

    def _enhance_package_json_for_lovable(self, package_json: Dict) -> Dict:
        """Enhance package.json for Lovable.dev projects"""

        # Ensure required scripts exist for React/Next.js
        scripts: Dict = package_json.setdefault("scripts", {})
        scripts.update(
            {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint",
                "test": "jest",
                "test:watch": "jest --watch",
                "storybook": "storybook dev -p 6006",
                "build-storybook": "storybook build",
                "type-check": "tsc --noEmit",
            }
        )

        # Add production dependencies for React/Next.js
        deps: Dict = package_json.setdefault("dependencies", {})
        deps.update(
            {
                "next": "^14.0.0",
                "react": "^18.0.0",
                "react-dom": "^18.0.0",
                "@next/font": "^14.0.0",
                "clsx": "^2.0.0",
            }
        )

        # Add development dependencies for TypeScript and testing
        dev_deps: Dict = package_json.setdefault("devDependencies", {})
        dev_deps.update(
            {
                "typescript": "^5.0.0",
                "@types/react": "^18.0.0",
                "@types/react-dom": "^18.0.0",
                "@types/node": "^20.0.0",
                "eslint": "^8.0.0",
                "eslint-config-next": "^14.0.0",
                "@testing-library/react": "^14.0.0",
                "@testing-library/jest-dom": "^6.0.0",
                "jest": "^29.0.0",
                "jest-environment-jsdom": "^29.0.0",
                "@storybook/react": "^7.0.0",
                "@storybook/addon-essentials": "^7.0.0",
                "tailwindcss": "^3.0.0",
                "autoprefixer": "^10.0.0",
                "postcss": "^8.0.0",
            }
        )

        # Add engines specification
        package_json["engines"] = {"node": ">=18.0.0", "npm": ">=8.0.0"}

        return package_json

    def _generate_replit_production_files(
        self, inputs: PrototypeEnhancerInputs
    ) -> Dict[str, str]:
        """Generate production files for Replit projects"""

        files: Dict[str, str] = {}

        # Environment configuration
        files[".env.example"] = (
            """
# Server Configuration
PORT=3000
NODE_ENV=production

# Database Configuration
DATABASE_URL=your_database_url_here

# API Keys
JWT_SECRET=your_jwt_secret_here
API_KEY=your_api_key_here

# Azure Configuration
AZURE_STORAGE_CONNECTION_STRING=your_azure_storage_connection_string
        """.strip()
        )

        # Production server configuration
        files["server.js"] = (
            """
const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const compression = require('compression');
const rateLimit = require('express-rate-limit');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Security middleware
app.use(helmet());
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
  credentials: true
}));

// Performance middleware
app.use(compression());

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});
app.use(limiter);

// Body parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Routes
app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Error handling
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

module.exports = app;
        """.strip()
        )

        # Process management configuration
        files["ecosystem.config.js"] = (
            """
module.exports = {
  apps: [{
    name: 'replit-app',
    script: 'server.js',
    instances: 'max',
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'development'
    },
    env_production: {
      NODE_ENV: 'production',
      PORT: 8080
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true
  }]
};
        """.strip()
        )

        return files

    def _generate_azure_configs(self, platform: str) -> Dict[str, str]:
        """Generate Azure-specific configuration files"""

        files: Dict[str, str] = {}

        # Azure App Service configuration
        files["web.config"] = (
            """
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="iisnode" path="server.js" verb="*" modules="iisnode"/>
    </handlers>
    <rewrite>
      <rules>
        <rule name="DynamicContent">
          <conditions>
            <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="True"/>
          </conditions>
          <action type="Rewrite" url="server.js"/>
        </rule>
      </rules>
    </rewrite>
    <security>
      <requestFiltering>
        <hiddenSegments>
          <remove segment="bin"/>
        </hiddenSegments>
      </requestFiltering>
    </security>
    <httpErrors existingResponse="PassThrough" />
  </system.webServer>
</configuration>
        """.strip()
        )

        # Azure DevOps pipeline
        files["azure-pipelines.yml"] = (
            f"""
trigger:
- main

pool:
  vmImage: 'ubuntu-latest'

variables:
  nodeVersion: '18.x'

stages:
- stage: Build
  jobs:
  - job: BuildAndTest
    steps:
    - task: NodeTool@0
      inputs:
        versionSpec: '$(nodeVersion)'
      displayName: 'Install Node.js'
    
    - script: npm ci
      displayName: 'Install dependencies'
    
    - script: npm run lint
      displayName: 'Run linting'
    
    - script: npm test
      displayName: 'Run tests'
    
    - script: npm run build
      displayName: 'Build application'
    
    - task: ArchiveFiles@2
      inputs:
        rootFolderOrFile: '.'
        includeRootFolder: false
        archiveType: 'zip'
        archiveFile: '$(Build.ArtifactStagingDirectory)/$(Build.BuildId).zip'
        replaceExistingArchive: true
    
    - task: PublishBuildArtifacts@1
      inputs:
        PathtoPublish: '$(Build.ArtifactStagingDirectory)'
        ArtifactName: '{platform}-app'

- stage: Deploy
  dependsOn: Build
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  jobs:
  - deployment: DeployToAzure
    environment: 'production'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureWebApp@1
            inputs:
              azureSubscription: 'Azure-Subscription'
              appType: 'webAppLinux'
              appName: '$(appName)'
              package: '$(Pipeline.Workspace)/**/*.zip'
              runtimeStack: 'NODE|18-lts'
        """.strip()
        )

        return files

    def _generate_testing_files(self, platform: str) -> Dict[str, str]:
        """Generate testing configuration files"""

        files: Dict[str, str] = {}

        # Jest configuration
        files["jest.config.js"] = (
            """
module.exports = {
  testEnvironment: 'node',
  collectCoverageFrom: [
    '**/*.{js,jsx}',
    '!**/node_modules/**',
    '!**/coverage/**',
    '!jest.config.js'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  testMatch: [
    '**/__tests__/**/*.js',
    '**/?(*.)+(spec|test).js'
  ]
};
        """.strip()
        )

        # Sample test file
        files["__tests__/server.test.js"] = (
            """
const request = require('supertest');
const app = require('../server');

describe('Server', () => {
  test('Health check endpoint', async () => {
    const response = await request(app)
      .get('/health')
      .expect(200);
    
    expect(response.body).toHaveProperty('status', 'OK');
    expect(response.body).toHaveProperty('timestamp');
  });
  
  test('Rate limiting', async () => {
    // Test rate limiting by making multiple requests
    const promises = Array(5).fill().map(() => 
      request(app).get('/health')
    );
    
    const responses = await Promise.all(promises);
    responses.forEach(response => {
      expect(response.status).toBe(200);
    });
  });
});
        """.strip()
        )

        # Playwright E2E configuration
        files["playwright.config.js"] = (
            """
module.exports = {
  testDir: './e2e',
  use: {
    baseURL: 'http://localhost:3000',
    headless: true
  },
  webServer: {
    command: 'npm start',
    port: 3000,
    reuseExistingServer: !process.env.CI
  },
  projects: [
    {
      name: 'chromium',
      use: { ...require('@playwright/test').devices['Desktop Chrome'] }
    },
    {
      name: 'firefox',
      use: { ...require('@playwright/test').devices['Desktop Firefox'] }
    }
  ]
};
        """.strip()
        )

        return files

    def _generate_security_files(self, platform: str) -> Dict[str, str]:
        """Generate security configuration files"""
        files: Dict[str, str] = {}

        # SECURITY.md
        files["SECURITY.md"] = (
            "# Security Policy\n"
            "\n"
            "## Reporting a Vulnerability\n"
            "Please report security issues by opening an issue or contacting the maintainers directly.\n"
            "\n"
            "## Best Practices\n"
            "- Use strong environment secrets\n"
            "- Keep dependencies up-to-date (`npm audit`)\n"
            "- Enable HTTP headers with helmet\n"
            "- Use rate limiting and input validation\n"
        )

        # .env.example with security vars
        files[".env.example"] = (
            "NODE_ENV=production\n"
            "PORT=3000\n"
            "JWT_SECRET=your-secure-jwt-secret\n"
            "SESSION_SECRET=your-session-secret\n"
            "RATE_LIMIT_WINDOW_MS=60000\n"
            "RATE_LIMIT_MAX=100\n"
        )

        # Example helmet.js middleware
        files["middleware/helmet.js"] = (
            "const helmet = require('helmet');\n"
            "\n"
            "module.exports = function(app) {\n"
            "  app.use(helmet());\n"
            "};\n"
        )

        # npm audit script
        files["scripts/security_audit.sh"] = (
            "#!/bin/bash\n"
            "echo 'Running npm audit...'\n"
            "npm audit --audit-level=moderate || echo 'Audit found some issues.'\n"
        )

        return files

    def _get_production_checklist(self, platform: str) -> List[str]:
        """Get production readiness checklist for platform"""

        common_checklist: List[str] = [
            "Environment variables configured",
            "Security headers implemented",
            "Rate limiting enabled",
            "Error handling implemented",
            "Logging configured",
            "Health check endpoint added",
            "HTTPS configured",
            "Database connections secured",
        ]

        platform_specific: Dict[str, List[str]] = {
            "replit": [
                "Replit configuration updated for production",
                "Node.js version specified in package.json",
                "PM2 or cluster mode configured",
            ],
            "lovable": [
                "TypeScript configurations optimized",
                "React components tested",
                "Bundle size optimized",
                "Accessibility tests passing",
            ],
            "bolt": [
                "Database migrations tested",
                "API documentation generated",
                "Container configuration validated",
                "Full-stack integration tests passing",
            ],
        }

        return common_checklist + platform_specific.get(platform, [])

    def _get_deployment_config(self, platform: str) -> Dict[str, Any]:
        """Get deployment configuration for platform"""

        base_config: Dict[str, Any] = {
            "type": "web_app",
            "runtime": "nodejs",
            "version": "18.x",
            "build_command": "npm run build",
            "start_command": "npm start",
            "environment_variables": ["NODE_ENV=production", "PORT=8080"],
            "health_check": "/health",
        }

        platform_configs: Dict[str, Dict[str, Any]] = {
            "replit": {
                "preferred_hosting": ["azure-app-service", "vercel", "railway"],
                "container_support": True,
                "auto_scaling": True,
            },
            "lovable": {
                "preferred_hosting": ["vercel", "netlify", "azure-static-web-apps"],
                "static_generation": True,
                "cdn_optimization": True,
            },
            "bolt": {
                "preferred_hosting": ["azure-container-instances", "railway", "render"],
                "database_required": True,
                "container_required": True,
            },
        }

        base_config.update(platform_configs.get(platform, {}))
        return base_config

    def _get_next_steps(self, platform: str, enhancement_type: str) -> List[str]:
        """Get recommended next steps after enhancement"""

        steps: List[str] = [
            "Review and test all enhanced files",
            "Update environment variables for production",
            "Run comprehensive test suite",
            "Deploy to staging environment",
            "Configure monitoring and alerts",
        ]

        platform_steps: Dict[str, List[str]] = {
            "replit": [
                "Test Replit → GitHub export workflow",
                "Configure Azure App Service deployment",
                "Setup PM2 for production process management",
            ],
            "lovable": [
                "Run Storybook for component documentation",
                "Execute accessibility testing suite",
                "Optimize bundle size and performance",
            ],
            "bolt": [
                "Test database migrations",
                "Validate API endpoints with documentation",
                "Run full-stack integration tests",
            ],
        }

        return steps + platform_steps.get(platform, [])

    def _generic_enhancement(
        self, inputs: PrototypeEnhancerInputs
    ) -> PrototypeEnhancerOutputs:
        """Generic enhancement for unknown platforms"""

        new_files: Dict[str, str] = {}

        # Add basic production files
        new_files[".env.example"] = "NODE_ENV=production\nPORT=3000"
        new_files["Dockerfile"] = self._generate_dockerfile("generic")

        return PrototypeEnhancerOutputs(
            enhanced_files={},
            new_files=new_files,
            enhancement_summary="Applied generic production enhancements",
            production_checklist=self._get_production_checklist("generic"),
            deployment_config=self._get_deployment_config("generic"),
            estimated_effort="1-2 hours manual work → 10 minutes automated",
            next_steps=[
                "Review platform-specific requirements",
                "Add appropriate testing",
                "Configure deployment",
            ],
        )

    def _generate_dockerfile(self, platform: str) -> str:
        """Generate Dockerfile for the platform"""

        if platform == "replit":
            return """
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 8080

USER node

CMD ["npm", "start"]
            """.strip()

        return """
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
        """.strip()

    def _generate_typescript_config(self, platform: str) -> str:
        """Generate a standard tsconfig.json for React/Next.js projects."""
        return (
            "{\n"
            '  "compilerOptions": {\n'
            '    "target": "es6",\n'
            '    "lib": ["dom", "dom.iterable", "esnext"],\n'
            '    "allowJs": true,\n'
            '    "skipLibCheck": true,\n'
            '    "esModuleInterop": true,\n'
            '    "allowSyntheticDefaultImports": true,\n'
            '    "strict": true,\n'
            '    "forceConsistentCasingInFileNames": true,\n'
            '    "module": "esnext",\n'
            '    "moduleResolution": "node",\n'
            '    "resolveJsonModule": true,\n'
            '    "isolatedModules": true,\n'
            '    "noEmit": true,\n'
            '    "jsx": "react-jsx"\n'
            "  },\n"
            '  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],\n'
            '  "exclude": ["node_modules"]\n'
            "}"
        )

    def _generate_next_config(self, platform: str) -> str:
        """Generate a basic next.config.js file."""
        return (
            "const nextConfig = {\n"
            "  reactStrictMode: true,\n"
            "  swcMinify: true,\n"
            "  images: {\n"
            "    domains: ['*'], // Adjust as needed\n"
            "  },\n"
            "};\n\n"
            "module.exports = nextConfig;\n"
        )

    def _generate_react_testing_setup(self) -> dict:
        """Generate minimal React testing setup (Jest + React Testing Library)."""
        return {
            "jest.config.js": (
                "module.exports = {\n"
                "  testEnvironment: 'jsdom',\n"
                "  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],\n"
                "  moduleNameMapper: {\n"
                "    '\\.(css|less|scss|sass)$': 'identity-obj-proxy'\n"
                "  }\n"
                "};\n"
            ),
            "jest.setup.js": ("import '@testing-library/jest-dom';\n"),
            "__tests__/App.test.tsx": (
                "import { render, screen } from '@testing-library/react';\n"
                "import App from '../pages/_app';\n\n"
                "test('renders without crashing', () => {\n"
                "  render(<App Component={() => <div>Test</div>} pageProps={{}} />);\n"
                "  expect(screen.getByText('Test')).toBeInTheDocument();\n"
                "});\n"
            ),
        }

    def _generate_storybook_config(self) -> dict:
        """Generate minimal Storybook configuration for React."""
        return {
            ".storybook/main.js": (
                "module.exports = {\n"
                "  stories: ['../components/**/*.stories.@(js|jsx|ts|tsx)'],\n"
                "  addons: [\n"
                "    '@storybook/addon-links',\n"
                "    '@storybook/addon-essentials',\n"
                "    '@storybook/addon-interactions',\n"
                "  ],\n"
                "  framework: '@storybook/react',\n"
                "};\n"
            ),
            ".storybook/preview.js": (
                "export const parameters = {\n"
                "  actions: { argTypesRegex: '^on[A-Z].*' },\n"
                "  controls: { expanded: true },\n"
                "};\n"
            ),
            "components/Button.stories.tsx": (
                "import React from 'react';\n"
                "import { Button } from './Button';\n\n"
                "export default {\n"
                "  title: 'Example/Button',\n"
                "  component: Button,\n"
                "};\n\n"
                "export const Primary = () => <Button>Primary</Button>;\n"
            ),
        }

    def _generate_accessibility_testing(self) -> dict:
        """Generate minimal accessibility testing setup (axe-core with Jest)."""
        return {
            "__tests__/a11y.test.tsx": (
                "import { render } from '@testing-library/react';\n"
                "import { axe, toHaveNoViolations } from 'jest-axe';\n"
                "expect.extend(toHaveNoViolations);\n\n"
                "test('main app is accessible', async () => {\n"
                "  const { container } = render(<main>Accessible Content</main>);\n"
                "  const results = await axe(container);\n"
                "  expect(results).toHaveNoViolations();\n"
                "});\n"
            ),
            "jest-axe.config.js": (
                "module.exports = {\n"
                "  rules: {\n"
                "    // Custom axe rules can be added here\n"
                "  }\n"
                "};\n"
            ),
        }

    def _generate_database_management(self, platform: str) -> Dict[str, str]:
        """Generate database management config and migration files."""
        files: Dict[str, str] = {}
        if platform in ("replit", "lovable", "bolt", "same", "emergent"):
            files["prisma/schema.prisma"] = (
                """
// Example Prisma schema for PostgreSQL
// Adjust for your DB provider

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id    Int    @id @default(autoincrement())
  email String @unique
  name  String?
}
                """.strip()
            )
            files["scripts/migrate.sh"] = (
                """
#!/bin/bash
# Run Prisma migrations
yarn prisma migrate deploy
                """.strip()
            )
        return files

    def _generate_api_documentation(self, platform: str) -> Dict[str, str]:
        """Generate API documentation setup (Swagger/OpenAPI)."""
        files: Dict[str, str] = {}
        if platform in ("replit", "lovable", "bolt", "same", "emergent"):
            files["docs/openapi.yaml"] = (
                """
openapi: 3.0.0
info:
  title: Example API
  version: 1.0.0
paths:
  /users:
    get:
      summary: List users
      responses:
        '200':
          description: A list of users
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        email:
          type: string
        name:
          type: string
                """.strip()
            )
            files["scripts/generate_api_docs.sh"] = (
                """
#!/bin/bash
# Generate static API docs from OpenAPI YAML
yarn swagger-cli bundle docs/openapi.yaml --outfile public/api-docs.json --type json
                """.strip()
            )
        return files

    def _generate_fullstack_testing(self, platform: str) -> Dict[str, str]:
        """Generate configuration for fullstack (integration/E2E) testing."""
        files: Dict[str, str] = {}
        if platform in ("replit", "lovable", "bolt", "same", "emergent"):
            files["playwright.config.js"] = (
                """
// Playwright config for E2E testing
module.exports = {
  testDir: './e2e',
  timeout: 30000,
  retries: 1,
  use: {
    headless: true,
    baseURL: 'http://localhost:3000',
  },
};
                """.strip()
            )
            files["e2e/example.spec.js"] = (
                """
const { test, expect } = require('@playwright/test');
test('homepage loads', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/Example/);
});
                """.strip()
            )
        return files

    def _generate_monitoring_config(self, platform: str) -> Dict[str, str]:
        """Generate monitoring config (Prometheus, Grafana, etc)."""
        files: Dict[str, str] = {}
        if platform in ("replit", "lovable", "bolt", "same", "emergent"):
            files["monitoring/prometheus.yml"] = (
                """
scrape_configs:
  - job_name: 'app'
    static_configs:
      - targets: ['localhost:3000']
                """.strip()
            )
            files["monitoring/grafana_dashboard.json"] = (
                """
{
  "dashboard": {
    "title": "App Monitoring",
    "panels": [
      {
        "type": "graph",
        "title": "HTTP Requests",
        "targets": [{"expr": "http_requests_total"}]
      }
    ]
  }
}
                """.strip()
            )
        return files

    def _generate_docker_compose(self, platform: str) -> Dict[str, str]:
        """Generate a docker-compose.yml for local development."""
        files: Dict[str, str] = {}
        if platform in ("replit", "lovable", "bolt", "same", "emergent"):
            files["docker-compose.yml"] = (
                """
version: '3.8'
services:
  app:
    build: .
    ports:
      - '3000:3000'
    env_file:
      - .env
    depends_on:
      - db
  db:
    image: postgres:13
    restart: always
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: appdb
    ports:
      - '5432:5432'
                """.strip()
            )
        return files

    def _generate_customization_framework(self, platform: str) -> Dict[str, str]:
        """Generate starter code for a customization/theming framework."""
        files: Dict[str, str] = {}
        if platform in ("lovable",):
            files["src/theme/index.ts"] = (
                """
// Theme provider for styled-components
import { ThemeProvider } from 'styled-components';
export const theme = {
  colors: {
    primary: '#0070f3',
    secondary: '#1c1c1e',
  },
};
export function withTheme(Component: any) {
  return (props: any) => (
    <ThemeProvider theme={theme}>
      <Component {...props} />
    </ThemeProvider>
  );
}
                """.strip()
            )
        return files

    def _generate_branding_system(self, platform: str) -> Dict[str, str]:
        """Generate starter branding config/assets."""
        files: Dict[str, str] = {}
        if platform in ("lovable",):
            files["public/branding/logo.svg"] = (
                """
<svg width=\"120\" height=\"40\" viewBox=\"0 0 120 40\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\">
  <rect width=\"120\" height=\"40\" rx=\"8\" fill=\"#0070f3\"/>
  <text x=\"60\" y=\"25\" fill=\"white\" font-size=\"20\" text-anchor=\"middle\" alignment-baseline=\"middle\">Brand</text>
</svg>
                """.strip()
            )
            files["src/branding/index.ts"] = (
                """
// Branding utilities
export const BRAND_NAME = 'Brand';
export const LOGO_PATH = '/branding/logo.svg';
                """.strip()
            )
        return files

    def _generate_feature_toggles(self, platform: str) -> Dict[str, str]:
        """Generate feature toggle setup (simple flags)."""
        files: Dict[str, str] = {}
        if platform in ("lovable", "replit", "bolt", "same", "emergent"):
            files["src/featureFlags.ts"] = (
                """
// Simple feature flag system
export const featureFlags = {
  newDashboard: false,
  betaFeature: false,
};
export function isFeatureEnabled(flag: string) {
  return !!featureFlags[flag];
}
                """.strip()
            )
        return files

    def _generate_deployment_automation(self, platform: str) -> Dict[str, str]:
        """Generate deployment automation scripts (GitHub Actions)."""
        files: Dict[str, str] = {}
        if platform in ("lovable", "replit", "bolt", "same", "emergent"):
            files[".github/workflows/deploy.yml"] = (
                """
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18.x'
      - name: Install dependencies
        run: yarn install --frozen-lockfile
      - name: Build
        run: yarn build
      - name: Deploy
        run: echo "Deploy step here"
                """.strip()
            )
        return files

    def _generate_monitoring_scripts(self, platform: str) -> Dict[str, str]:
        """Generate monitoring scripts (health checks, alerts)."""
        files: Dict[str, str] = {}
        if platform in ("lovable", "replit", "bolt", "same", "emergent"):
            files["scripts/health_check.sh"] = (
                """
#!/bin/bash
# Health check script
curl -f http://localhost:3000/health || exit 1
                """.strip()
            )
            files["scripts/alert_on_failure.sh"] = (
                """
#!/bin/bash
# Alert script (stub)
echo "ALERT: Health check failed!" | mail -s "App Down" admin@example.com
                """.strip()
            )
        return files

    def _generate_backup_scripts(self, platform: str) -> Dict[str, str]:
        """Generate backup scripts for database/files."""
        files: Dict[str, str] = {}
        if platform in ("lovable", "replit", "bolt", "same", "emergent"):
            files["scripts/backup_db.sh"] = (
                """
#!/bin/bash
# Backup database script
docker exec app-db pg_dump -U user appdb > backup.sql
                """.strip()
            )
            files["scripts/restore_db.sh"] = (
                """
#!/bin/bash
# Restore database script
docker exec -i app-db psql -U user appdb < backup.sql
                """.strip()
            )
        return files


# Entry point for AutoPR
def run(inputs_dict: dict) -> dict:
    """AutoPR entry point"""
    inputs = PrototypeEnhancerInputs(**inputs_dict)
    enhancer = PrototypeEnhancer()
    outputs = enhancer.enhance_prototype(inputs)
    return outputs.dict()


if __name__ == "__main__":
    # Test the action
    sample_inputs = {
        "platform": "replit",
        "project_files": {
            "package.json": '{"name": "my-app", "dependencies": {"express": "^4.18.0"}}'
        },
        "enhancement_type": "production_ready",
        "target_environment": "production",
    }

    result = run(sample_inputs)
    print(json.dumps(result, indent=2))
