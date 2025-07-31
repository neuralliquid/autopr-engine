# {{ platform_name }} Platform Guide

> *Generated on {{ generation_date }}*

## Overview

{{ platform_info.description }}

### Key Features

{% for feature in key_features %}

- {{ feature }}

{% endfor %}

{% if pricing %}

### Pricing

{% for tier, details in pricing.items() %}

- **{{ tier.title() }}**: {{ details }}

{% endfor %}
{% endif %}

## Configuration Options

{% for var_name, var_info in variables.items() %}

### {{ var_name.replace('_', ' ').title() }}

- **Type**: {{ var_info.get('type', 'string') }}
- **Required**: {{ "Required" if var_info.get('required', False) else "Optional" }}
- **Description**: {{ var_info.get('description', '') }}

{% if var_info.get('examples') %}
**Examples**:
{% for example in var_info.examples %}

- `{{ example }}`

{% endfor %}
{% endif %}

{% endfor %}

{% if development_approach %}

## Development Approach

**Method**: {{ development_approach.get('method', 'Not specified') }}

{{ development_approach.get('description', '') }}

{% if development_approach.get('steps') %}

### Development Steps

{% for step in development_approach.steps %}
{{ loop.index }}. {{ step }}
{% endfor %}
{% endif %}
{% endif %}

{% if best_practices %}

## Best Practices

{% for category, practices in best_practices.items() %}

### {{ category.replace('_', ' ').title() }}

{% if practices is iterable and practices is not string %}
{% for practice in practices %}

- {{ practice }}

{% endfor %}
{% else %}
{{ practices }}
{% endif %}

{% endfor %}
{% endif %}

{% if troubleshooting %}

## Troubleshooting

{% for issue, solution in troubleshooting.items() %}

### {{ issue.replace('_', ' ').title() }}

{{ solution }}

{% endfor %}
{% endif %}

## Getting Started

1. **Choose Your Template**: Select from the available {{ platform_name }} templates
2. **Configure Variables**: Set up the required configuration options above
3. **Deploy**: Follow the platform-specific deployment guide
4. **Customize**: Modify the template to match your specific needs

## Additional Resources

- [{{ platform_name }} Official Documentation]({{ platform_info.get('documentation_url', '#') }})
- [Template Examples](examples/)
- [Community Support]({{ platform_info.get('community_url', '#') }})

---

*Need help? Check our [troubleshooting guide](troubleshooting.md) or [contact support](support.md).*
