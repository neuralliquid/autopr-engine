# AutoPR Template System

This directory contains the comprehensive template system for the AutoPR engine, supporting **no-code**, **vibe
coding**, and **AI agent builder** platforms with a hybrid YAML + template approach.

## Template System Overview

The AutoPR template system uses a **hybrid YAML + template approach** that combines:

- **Rich metadata** (variables, variants, usage guidelines)
- **Template content** with variable substitution
- **Platform-specific configurations** for 46+ platforms
- **Reusable components** (security, deployment, testing, monitoring)

## Directory Structure

### `/platforms/`

Platform-specific templates for no-code, vibe coding, and AI agent builder platforms:

**Tier 1 Platforms:**

- `horizons/` - Hostinger Horizons (vibe coding leader)
- `lovable/` - Lovable.dev (rapid development)
- `bubble/` - Bubble (complex web apps)
- `glide/` - Glide (data-driven apps)
- `n8n/` - n8n (AI agent workflows)
- `make/` - Make.com (no-code automation)
- `google-adk/` - Google Agent Development Kit
- `gemini-cli/` - Google Gemini CLI
- `google-opal/` - Google Opal AI mini-apps

**Tier 2 & 3 Platforms:**

- `replit/`, `thunkable/`, `flutterflow/`, `appsmith/`, `retool/`, `power-apps/`
- `webflow/`, `framer/`, `supabase/`, `firebase/`, `airtable/`
- `flowise/`, `gumloop/`, `bildr/`, `backendless/`, `zapier-interfaces/`
- And 20+ more platforms...

### `/security/` ✨ **Extracted YAML Templates**

Security configuration templates with metadata and variants:

- `helmet.config.yml` - Express.js Helmet security middleware
- `cors.config.yml` - CORS configuration with environment variants
- `htaccess.yml` - Apache .htaccess with SPA routing & security headers

### `/deployment/` ✨ **Extracted YAML Templates**

Deployment pipeline templates with CI/CD configurations:

- `github-actions.yml` - GitHub Actions workflows (React, Node.js, Azure, Vercel)
- `azure-pipeline.yml` - Azure DevOps pipelines (App Service, Static Web Apps, Functions)
- `azure-static-web-app.json` - Azure Static Web Apps configuration

### `/build/` ✨ **Extracted YAML Templates**

Build configuration templates with optimization and variants:

- `pm2.config.yml` - PM2 process manager with clustering and monitoring
- `vite-enhanced.config.yml` - Optimized Vite with PWA, compression, and performance
- `vite.config.js` - Basic Vite configuration (legacy)
- `vitest.config.js` - Vitest testing configuration (legacy)
- `next.config.js` - Next.js configuration (legacy)

### `/testing/` ✨ **Extracted YAML Templates**

Testing setup and component templates:

- `test-setup.yml` - Comprehensive test setup (Jest/Vitest, mocks, utilities)
- `error-boundary.yml` - Production-ready React Error Boundary component
- `playwright.config.ts` - Playwright E2E testing (legacy)
- `setupTests.ts` - Basic test setup (legacy)

### `/monitoring/` ✨ **Extracted YAML Templates**

Monitoring and health check templates:

- `health-check.yml` - Comprehensive health check script with database/API checks
- `backup.sh` - Backup script (legacy)
- `monitor.sh` - System monitoring script (legacy)
- `restore.sh` - Restore script (legacy)

### `/docker/` 🔄 **Partially Extracted**

Docker configuration templates:

- `react.dockerfile.yml` - React application Dockerfile (YAML)
- `node.dockerfile.yml` - Node.js application Dockerfile (YAML)
- `react.dockerfile` - React Dockerfile (legacy)
- `node.dockerfile` - Node.js Dockerfile (legacy)
- `generic.dockerfile` - Generic Dockerfile (legacy)

### `/typescript/` 📁 **Legacy Static Files**

TypeScript configuration templates (static JSON files):

- `react-tsconfig.json` - React TypeScript configuration
- `vite-tsconfig.json` - Vite TypeScript configuration
- `basic-tsconfig.json` - Basic TypeScript configuration

### `/integrations/`

Cross-platform integration templates:

- `auth-integration.yml` - Authentication integration patterns
- `payment-integration.yml` - Payment system integration

### `/use-cases/`

Specialized use case templates:

- `e-commerce-store.yml` - E-commerce application template
- `social-platform.yml` - Social media platform template
- `project-management.yml` - Project management application

### `/discovery/`

Documentation and migration guides:

- `migration_guide.yml` - Platform migration guidance
- `platform_comparison.yml` - Platform comparison matrix

## Template System Features

### ✨ **Hybrid YAML + Template Approach**

Each extracted template includes:

```yaml
name: "Template Name"
category: "template_category"
description: "Template description"
version: "1.0.0"
author: "AutoPR Template System"
tags: ["tag1", "tag2"]

template_info:
  name: "Display Name"
  type: "configuration_type"
  framework: "target_framework"
  target_audience: "developers, engineers"
  primary_use_cases: ["use_case_1", "use_case_2"]

variables:
  variable_name:
    type: "string|boolean|select|array"
    description: "Variable description"
    default: "default_value"
    required: true|false

variants:
  variant_name:
    description: "Variant description"
    variables:
      variable_name: "variant_value"

usage:
  getting_started: ["step1", "step2"]
  best_practices: ["practice1", "practice2"]
  limitations: ["limitation1", "limitation2"]

template: |
  # Template content with {{ variable }} substitution
```

### 🎯 **Platform Coverage**

- **46+ platforms** across no-code, vibe coding, and AI agent builders
- **Tier 1**: Industry leaders (Horizons, Lovable, Bubble, n8n, Make.com)
- **Tier 2**: Specialized platforms (Webflow, Retool, Flowise)
- **Tier 3**: Emerging and niche platforms

### 🔧 **Template Categories**

- `no_code_platform` - Traditional drag-and-drop platforms
- `vibe_coding_platform` - Conversational AI development
- `ai_agent_builder` - Intelligent automation and multi-agent systems
- `security` - Security configurations and headers
- `deployment` - CI/CD pipelines and deployment
- `build` - Build tools and optimization
- `testing` - Test setup and components
- `monitoring` - Health checks and monitoring

## Usage

### FileGenerator Integration

```python
from autopr.actions.prototype_enhancement.file_generators import FileGenerator

generator = FileGenerator()

# Generate from extracted YAML template
content = generator.generate_from_template(
    template_key="security/helmet.config.yml",
    variables={"content_security_policy": True},
    variants=["production"]
)

# List available templates
templates = generator.list_available_templates(category="security")

# Get template metadata
info = generator.get_template_info("deployment/github-actions.yml")
```

### Template Development

1. **Create YAML template** with metadata and variables
2. **Define variants** for different use cases
3. **Add usage documentation** and best practices
4. **Test template generation** with various variable combinations
5. **Update FileGenerator** to reference new template

## Migration Status

### ✅ **Completed Extractions**

- Security configurations (helmet, CORS, .htaccess)
- Deployment pipelines (GitHub Actions, Azure DevOps)
- Build configurations (PM2, enhanced Vite)
- Testing setups (test setup, error boundary)
- Monitoring scripts (health check)

### 🔄 **In Progress**

- Docker configurations (partial YAML extraction)
- Additional deployment targets (Vercel, Netlify)
- Enhanced TypeScript configurations

### 📋 **Remaining Hardcoded Templates**

Still in Python files and need extraction:

- `file_generators.py`: Next.js config, web.config, static web app config
- `enhancement_strategies.py`: Platform-specific configurations

## Quality Assurance

All templates are validated using the integrated QA framework:

- **Metadata completeness** (95%+ score required)
- **Variable validation** and type checking
- **Template syntax** verification
- **Usage documentation** quality
- **Best practices** compliance

Run QA validation:

```bash
python templates/discovery/qa_framework.py
```

## Contributing

1. Follow the **hybrid YAML + template** format
2. Include comprehensive **metadata and variants**
3. Add **usage documentation** and best practices
4. Test with **multiple variable combinations**
5. Validate with **QA framework** before submission

For detailed guidelines, see the [Template Development Guide](discovery/docs_generator.py).
