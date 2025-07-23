"""
AutoPR Action: Prototype Enhancer
Enhances prototypes based on detected platform for production readiness
"""

import json
import os
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime

class PrototypeEnhancerInputs(BaseModel):
    platform: str
    project_files: Dict[str, str] = {}
    enhancement_type: str = "production_ready"  # "production_ready", "testing", "security", "performance"
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
    def __init__(self):
        self.enhancement_strategies = {
            'replit': self._enhance_replit_project,
            'lovable': self._enhance_lovable_project,
            'bolt': self._enhance_bolt_project,
            'same': self._enhance_same_project,
            'emergent': self._enhance_emergent_project
        }
        
        # Common production enhancements
        self.common_enhancements = {
            'security': [
                'helmet', 'cors', 'express-rate-limit', 'bcryptjs',
                'jsonwebtoken', 'express-validator'
            ],
            'performance': [
                'compression', 'morgan', 'cluster', 'pm2'
            ],
            'monitoring': [
                '@azure/monitor-opentelemetry-exporter', 'winston',
                'express-prometheus-middleware'
            ],
            'testing': [
                'jest', '@testing-library/react', '@testing-library/jest-dom',
                'playwright', 'supertest'
            ]
        }

    def enhance_prototype(self, inputs: PrototypeEnhancerInputs) -> PrototypeEnhancerOutputs:
        """Enhance prototype for production readiness"""
        
        if inputs.platform in self.enhancement_strategies:
            return self.enhancement_strategies[inputs.platform](inputs)
        else:
            return self._generic_enhancement(inputs)

    def _enhance_replit_project(self, inputs: PrototypeEnhancerInputs) -> PrototypeEnhancerOutputs:
        """Enhance Replit-generated project"""
        
        enhanced_files = {}
        new_files = {}
        
        # Enhance package.json for production
        if 'package.json' in inputs.project_files:
            package_json = json.loads(inputs.project_files['package.json'])
            enhanced_package = self._enhance_package_json_for_replit(package_json)
            enhanced_files['package.json'] = json.dumps(enhanced_package, indent=2)
        
        # Add production configuration files
        new_files.update(self._generate_replit_production_files(inputs))
        
        # Add Azure-specific configurations
        new_files.update(self._generate_azure_configs('replit'))
        
        # Add testing configuration
        if inputs.enhancement_type in ['testing', 'production_ready']:
            new_files.update(self._generate_testing_files('replit'))
        
        # Add security enhancements
        if inputs.enhancement_type in ['security', 'production_ready']:
            new_files.update(self._generate_security_files('replit'))
        
        production_checklist = self._get_production_checklist('replit')
        deployment_config = self._get_deployment_config('replit')
        
        return PrototypeEnhancerOutputs(
            enhanced_files=enhanced_files,
            new_files=new_files,
            enhancement_summary=f"Enhanced Replit project for {inputs.target_environment} deployment with security, testing, and monitoring",
            production_checklist=production_checklist,
            deployment_config=deployment_config,
            estimated_effort="2-4 hours manual work → 15 minutes automated",
            next_steps=self._get_next_steps('replit', inputs.enhancement_type)
        )

    def _enhance_lovable_project(self, inputs: PrototypeEnhancerInputs) -> PrototypeEnhancerOutputs:
        """Enhance Lovable.dev project"""
        
        enhanced_files = {}
        new_files = {}
        
        # Enhance for React/TypeScript best practices
        if 'package.json' in inputs.project_files:
            package_json = json.loads(inputs.project_files['package.json'])
            enhanced_package = self._enhance_package_json_for_lovable(package_json)
            enhanced_files['package.json'] = json.dumps(enhanced_package, indent=2)
        
        # Add TypeScript configurations
        new_files['tsconfig.json'] = self._generate_typescript_config('lovable')
        new_files['next.config.js'] = self._generate_next_config('lovable')
        
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
            production_checklist=self._get_production_checklist('lovable'),
            deployment_config=self._get_deployment_config('lovable'),
            estimated_effort="3-6 hours manual work → 20 minutes automated",
            next_steps=self._get_next_steps('lovable', inputs.enhancement_type)
        )

    def _enhance_bolt_project(self, inputs: PrototypeEnhancerInputs) -> PrototypeEnhancerOutputs:
        """Enhance Bolt.new full-stack project"""
        
        enhanced_files = {}
        new_files = {}
        
        # Add database management
        new_files.update(self._generate_database_management())
        
        # Add API documentation
        new_files.update(self._generate_api_documentation())
        
        # Add full-stack testing
        new_files.update(self._generate_fullstack_testing())
        
        # Add monitoring and logging
        new_files.update(self._generate_monitoring_config('bolt'))
        
        # Add Docker configurations
        new_files['Dockerfile'] = self._generate_dockerfile('bolt')
        new_files['docker-compose.yml'] = self._generate_docker_compose('bolt')
        
        return PrototypeEnhancerOutputs(
            enhanced_files=enhanced_files,
            new_files=new_files,
            enhancement_summary="Enhanced Bolt.new project with database management, API docs, monitoring, and containerization",
            production_checklist=self._get_production_checklist('bolt'),
            deployment_config=self._get_deployment_config('bolt'),
            estimated_effort="4-8 hours manual work → 25 minutes automated",
            next_steps=self._get_next_steps('bolt', inputs.enhancement_type)
        )

    def _enhance_same_project(self, inputs: PrototypeEnhancerInputs) -> PrototypeEnhancerOutputs:
        """Enhance Same.new cloned project"""
        
        enhanced_files = {}
        new_files = {}
        
        # Add customization framework
        new_files.update(self._generate_customization_framework())
        
        # Add branding system
        new_files.update(self._generate_branding_system())
        
        # Add feature toggle system
        new_files.update(self._generate_feature_toggles())
        
        return PrototypeEnhancerOutputs(
            enhanced_files=enhanced_files,
            new_files=new_files,
            enhancement_summary="Enhanced Same.new project with customization framework and feature management",
            production_checklist=self._get_production_checklist('same'),
            deployment_config=self._get_deployment_config('same'),
            estimated_effort="2-4 hours manual work → 20 minutes automated",
            next_steps=self._get_next_steps('same', inputs.enhancement_type)
        )

    def _enhance_emergent_project(self, inputs: PrototypeEnhancerInputs) -> PrototypeEnhancerOutputs:
        """Enhance Emergent.sh automation project"""
        
        enhanced_files = {}
        new_files = {}
        
        # Add advanced deployment scripts
        new_files.update(self._generate_deployment_automation())
        
        # Add monitoring scripts
        new_files.update(self._generate_monitoring_scripts())
        
        # Add backup and recovery
        new_files.update(self._generate_backup_scripts())
        
        return PrototypeEnhancerOutputs(
            enhanced_files=enhanced_files,
            new_files=new_files,
            enhancement_summary="Enhanced Emergent.sh project with advanced DevOps automation",
            production_checklist=self._get_production_checklist('emergent'),
            deployment_config=self._get_deployment_config('emergent'),
            estimated_effort="3-6 hours manual work → 30 minutes automated",
            next_steps=self._get_next_steps('emergent', inputs.enhancement_type)
        )

    def _enhance_package_json_for_replit(self, package_json: Dict) -> Dict:
        """Enhance package.json for Replit projects"""
        
        # Ensure required scripts exist
        scripts = package_json.setdefault('scripts', {})
        scripts.update({
            'start': 'node index.js',
            'dev': 'nodemon index.js',
            'build': 'echo "Build step for production"',
            'test': 'jest',
            'test:watch': 'jest --watch',
            'lint': 'eslint .',
            'lint:fix': 'eslint . --fix'
        })
        
        # Add production dependencies
        deps = package_json.setdefault('dependencies', {})
        deps.update({
            'helmet': '^7.0.0',
            'cors': '^2.8.5', 
            'compression': '^1.7.4',
            'dotenv': '^16.0.0',
            'express-rate-limit': '^6.7.0'
        })
        
        # Add development dependencies
        dev_deps = package_json.setdefault('devDependencies', {})
        dev_deps.update({
            'nodemon': '^2.0.22',
            'jest': '^29.5.0',
            'eslint': '^8.42.0',
            'prettier': '^2.8.8'
        })
        
        # Add engines specification
        package_json['engines'] = {
            'node': '>=18.0.0',
            'npm': '>=8.0.0'
        }
        
        return package_json

    def _generate_replit_production_files(self, inputs: PrototypeEnhancerInputs) -> Dict[str, str]:
        """Generate production files for Replit projects"""
        
        files = {}
        
        # Environment configuration
        files['.env.example'] = """
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
        
        # Production server configuration
        files['server.js'] = """
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
        
        # Process management configuration
        files['ecosystem.config.js'] = """
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
        
        return files

    def _generate_azure_configs(self, platform: str) -> Dict[str, str]:
        """Generate Azure-specific configuration files"""
        
        files = {}
        
        # Azure App Service configuration
        files['web.config'] = """
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
        
        # Azure DevOps pipeline
        files['azure-pipelines.yml'] = f"""
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
        
        return files

    def _generate_testing_files(self, platform: str) -> Dict[str, str]:
        """Generate testing configuration files"""
        
        files = {}
        
        # Jest configuration
        files['jest.config.js'] = """
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
        
        # Sample test file
        files['__tests__/server.test.js'] = """
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
        
        # Playwright E2E configuration
        files['playwright.config.js'] = """
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
        
        return files

    def _get_production_checklist(self, platform: str) -> List[str]:
        """Get production readiness checklist for platform"""
        
        common_checklist = [
            "Environment variables configured",
            "Security headers implemented", 
            "Rate limiting enabled",
            "Error handling implemented",
            "Logging configured",
            "Health check endpoint added",
            "HTTPS configured",
            "Database connections secured"
        ]
        
        platform_specific = {
            'replit': [
                "Replit configuration updated for production",
                "Node.js version specified in package.json",
                "PM2 or cluster mode configured"
            ],
            'lovable': [
                "TypeScript configurations optimized",
                "React components tested",
                "Bundle size optimized",
                "Accessibility tests passing"
            ],
            'bolt': [
                "Database migrations tested",
                "API documentation generated",
                "Container configuration validated",
                "Full-stack integration tests passing"
            ]
        }
        
        return common_checklist + platform_specific.get(platform, [])

    def _get_deployment_config(self, platform: str) -> Dict[str, Any]:
        """Get deployment configuration for platform"""
        
        base_config = {
            'type': 'web_app',
            'runtime': 'nodejs',
            'version': '18.x',
            'build_command': 'npm run build',
            'start_command': 'npm start',
            'environment_variables': [
                'NODE_ENV=production',
                'PORT=8080'
            ],
            'health_check': '/health'
        }
        
        platform_configs = {
            'replit': {
                'preferred_hosting': ['azure-app-service', 'vercel', 'railway'],
                'container_support': True,
                'auto_scaling': True
            },
            'lovable': {
                'preferred_hosting': ['vercel', 'netlify', 'azure-static-web-apps'],
                'static_generation': True,
                'cdn_optimization': True
            },
            'bolt': {
                'preferred_hosting': ['azure-container-instances', 'railway', 'render'],
                'database_required': True,
                'container_required': True
            }
        }
        
        base_config.update(platform_configs.get(platform, {}))
        return base_config

    def _get_next_steps(self, platform: str, enhancement_type: str) -> List[str]:
        """Get recommended next steps after enhancement"""
        
        steps = [
            "Review and test all enhanced files",
            "Update environment variables for production",
            "Run comprehensive test suite",
            "Deploy to staging environment",
            "Configure monitoring and alerts"
        ]
        
        platform_steps = {
            'replit': [
                "Test Replit → GitHub export workflow",
                "Configure Azure App Service deployment",
                "Setup PM2 for production process management"
            ],
            'lovable': [
                "Run Storybook for component documentation",
                "Execute accessibility testing suite",
                "Optimize bundle size and performance"
            ],
            'bolt': [
                "Test database migrations",
                "Validate API endpoints with documentation",
                "Run full-stack integration tests"
            ]
        }
        
        return steps + platform_steps.get(platform, [])

    def _generic_enhancement(self, inputs: PrototypeEnhancerInputs) -> PrototypeEnhancerOutputs:
        """Generic enhancement for unknown platforms"""
        
        new_files = {}
        
        # Add basic production files
        new_files['.env.example'] = "NODE_ENV=production\nPORT=3000"
        new_files['Dockerfile'] = self._generate_dockerfile('generic')
        
        return PrototypeEnhancerOutputs(
            enhanced_files={},
            new_files=new_files,
            enhancement_summary="Applied generic production enhancements",
            production_checklist=self._get_production_checklist('generic'),
            deployment_config=self._get_deployment_config('generic'),
            estimated_effort="1-2 hours manual work → 10 minutes automated",
            next_steps=["Review platform-specific requirements", "Add appropriate testing", "Configure deployment"]
        )

    def _generate_dockerfile(self, platform: str) -> str:
        """Generate Dockerfile for the platform"""
        
        if platform == 'replit':
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
        "target_environment": "production"
    }
    
    result = run(sample_inputs)
    print(json.dumps(result, indent=2)) 