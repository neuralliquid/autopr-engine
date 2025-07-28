#!/usr/bin/env python3
"""
Demonstration of Hybrid YAML + Template Approach
Shows how the enhanced FileGenerator works with metadata-driven templates.
"""

import json
import os
import sys
from pathlib import Path

# Add the autopr package to the path
sys.path.insert(0, str(Path(__file__).parent))

from autopr.actions.prototype_enhancement.file_generators import FileGenerator


def demo_hybrid_templates() -> None:
    """Demonstrate the hybrid YAML + template approach."""
    print("🚀 Hybrid YAML + Template Approach Demo")
    print("=" * 50)

    # Initialize the enhanced FileGenerator
    generator = FileGenerator()

    print("\n📋 Available Templates:")
    print("-" * 30)

    # List all available templates
    all_templates = generator.list_available_templates()
    for template in sorted(all_templates):
        print(f"  • {template}")

    print(f"\nTotal templates: {len(all_templates)}")

    # Show platform-specific templates
    print("\n🎯 Platform-Specific Templates:")
    print("-" * 35)

    platforms = ["replit", "lovable", "bolt"]
    for platform in platforms:
        templates = generator.list_available_templates(platform=platform)
        print(f"  {platform}: {len(templates)} templates")
        for template in templates[:3]:  # Show first 3
            print(f"    - {template}")
        if len(templates) > 3:
            print(f"    ... and {len(templates) - 3} more")

    # Show category-specific templates
    print("\n📁 Templates by Category:")
    print("-" * 30)

    categories = ["docker", "typescript", "testing"]
    for category in categories:
        templates = generator.list_available_templates(category=category)
        print(f"  {category}: {templates}")

    # Demonstrate template info
    print("\n📊 Template Information Example:")
    print("-" * 40)

    template_key = "docker/react.dockerfile"
    info = generator.get_template_info(template_key)
    if info:
        print(f"Template: {template_key}")
        print(f"Name: {info['name']}")
        print(f"Description: {info['description']}")
        print(f"Platforms: {info['platforms']}")
        print(f"Variables: {list(info['variables'].keys())}")
        print(f"Variants: {list(info['variants'].keys())}")

    # Demonstrate basic generation
    print("\n🔧 Basic Template Generation:")
    print("-" * 35)

    # Generate a basic React Dockerfile
    dockerfile_content = generator.generate_from_template(
        "docker/react.dockerfile",
        variables={"node_version": "20", "build_command": "npm run build"},
    )

    if dockerfile_content:
        print("Generated React Dockerfile (first 10 lines):")
        lines = dockerfile_content.split("\n")
        for i, line in enumerate(lines[:10], 1):
            print(f"  {i:2d}: {line}")
        if len(lines) > 10:
            print(f"  ... and {len(lines) - 10} more lines")

    # Demonstrate variant generation
    print("\n🎨 Template with Variants:")
    print("-" * 30)

    dockerfile_with_variants = generator.generate_from_template(
        "docker/react.dockerfile",
        variables={"node_version": "20"},
        variants=["with_nginx_config", "with_env_vars"],
    )

    if dockerfile_with_variants:
        print("Generated React Dockerfile with variants (first 15 lines):")
        lines = dockerfile_with_variants.split("\n")
        for i, line in enumerate(lines[:15], 1):
            print(f"  {i:2d}: {line}")

    # Demonstrate platform-specific generation
    print("\n🌐 Platform-Specific Generation:")
    print("-" * 40)

    platforms_to_test = ["replit", "lovable", "bolt"]
    for platform in platforms_to_test:
        print(f"\n{platform.upper()} Platform:")

        # Generate Dockerfile
        dockerfile = generator.generate_dockerfile(platform, variables={"node_version": "18"})
        print(f"  Dockerfile: {len(dockerfile.split()) if dockerfile else 0} words")

        # Generate TypeScript config
        tsconfig = generator.generate_typescript_config(platform, variables={"target": "ES2020"})
        print(f"  TypeScript config: {len(tsconfig.split()) if tsconfig else 0} words")

        # Generate testing files
        testing_files = generator.generate_testing_files(
            platform, variables={"coverage_threshold": 85}
        )
        print(f"  Testing files: {len(testing_files)} files")
        for filename in testing_files.keys():
            print(f"    - {filename}")

    # Demonstrate fallback behavior
    print("\n🔄 Fallback Behavior:")
    print("-" * 25)

    # Disable hybrid templates to show fallback
    generator.use_hybrid_templates = False
    fallback_dockerfile = generator.generate_dockerfile("replit")
    print(
        f"Fallback Dockerfile: {len(fallback_dockerfile.split()) if fallback_dockerfile else 0} words"
    )

    # Re-enable hybrid templates
    generator.use_hybrid_templates = True
    hybrid_dockerfile = generator.generate_dockerfile("replit")
    print(f"Hybrid Dockerfile: {len(hybrid_dockerfile.split()) if hybrid_dockerfile else 0} words")

    print("\n✅ Demo completed successfully!")
    print("\nKey Benefits of Hybrid Approach:")
    print("  • Rich metadata for templates")
    print("  • Variable substitution")
    print("  • Template variants")
    print("  • Platform-specific filtering")
    print("  • Backward compatibility")
    print("  • IDE support for template files")


def demo_template_creation() -> None:
    """Demonstrate how to create new templates."""
    print("\n📝 Creating New Templates:")
    print("-" * 30)

    # Example of creating a new template metadata file
    new_template_metadata = {
        "name": "Express.js API Template",
        "description": "Complete Express.js API server with middleware",
        "category": "backend",
        "platforms": ["replit", "same"],
        "file_extension": "js",
        "variables": {
            "port": {"type": "string", "default": "3000", "description": "Server port"},
            "cors_origin": {
                "type": "string",
                "default": "http://localhost:3000",
                "description": "CORS origin URL",
            },
        },
        "variants": {
            "with_auth": {
                "name": "With Authentication",
                "description": "Includes JWT authentication middleware",
                "modifications": [
                    {
                        "line": 5,
                        "action": "add_after",
                        "content": "const jwt = require('jsonwebtoken');",
                    }
                ],
            }
        },
        "usage": ["REST API servers", "Backend services", "Microservices"],
        "dependencies": {
            "required": ["express", "cors", "helmet"],
            "optional": ["jsonwebtoken", "bcrypt"],
        },
    }

    print("Example template metadata structure:")
    print(json.dumps(new_template_metadata, indent=2))


if __name__ == "__main__":
    try:
        demo_hybrid_templates()
        demo_template_creation()
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()
