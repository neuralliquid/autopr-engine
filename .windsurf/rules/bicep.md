---
trigger: glob
globs: **/*.bicep
---

Best Practices
Declarative and DRY: Use Bicep modules to encapsulate reusable pieces of infrastructure. Rather than copy-pasting
resource definitions, factor them into parameterized modules and use module calls. This keeps templates DRY and easier to manage. For example, create a storage.bicep module for storage account deployment and reuse it with different parameters for dev/prod. Organize Bicep files logically – e.g. one main bicep per environment or solution, with modules for complex resources (networking, compute, etc.).
Parameters and Variables: Define parameters for all environment-specific or configurable values (resource names,
sizing, toggle features) so the same template can be used in dev, test, prod with different parameter files. Use clear, descriptive names for parameters and avoid abbreviations
learn.microsoft.com
. Provide default values where it’s safe (prefer defaults that are cost-effective and secure, e.g. a SKU of a lower tier)
learn.microsoft.com
. Leverage Bicep’s type system for parameters (e.g. use string, int, bool appropriately or more complex types like
arrays/objects as needed), and use the @allowed decorator sparingly – only when a value truly must be one of a set (overusing @allowed can cause deployments to break when new valid values emerge)
learn.microsoft.com
. Use variables to hold complex expressions or repeated values to avoid cluttering resource definitions.
Resource Naming and Organization: Follow a consistent naming convention for Azure resources (consider adopting your
organization’s naming standard or Azure’s recommendations). In Bicep, the symbolic name of a resource is not the actual Azure name – avoid including “name” or type in the symbolic name
learn.microsoft.com
 (e.g., use appServicePlan instead of appServicePlanName as the symbolic name). Use lower camelCase for symbolic names
 per Bicep conventions
learn.microsoft.com
. Construct actual resource name properties using parameters and unique strings – for example, include environment or
location codes and use Bicep’s string interpolation and uniqueString() for uniqueness
learn.microsoft.com
. This ensures deployments are idempotent and resource names are unique across environments (uniqueString with resource
group ID helps achieve consistent uniqueness across deployments)
learn.microsoft.com
. Group related resources in the template using comments or regions, and deploy in a logical order (though Bicep
determines order by dependencies, grouping them conceptually helps readability).
Linting and Formatting
Bicep Linter: Enable the Bicep linter (built into the Bicep CLI/VS Code extension) to catch syntax errors and best
practice violations
learn.microsoft.com
. The linter will warn you about things like hardcoded credentials or locations, missing tags, using older API
versions, etc. – treat these as guidance to improve your template. Customize the linter rules via a bicepconfig.json if needed to fit your org’s standards (for example, you might enforce certain tags on all resources). Run bicep build (or az bicep build) regularly; it not only compiles your Bicep to ARM JSON to validate syntax but can also be coupled with bicep lint to enforce rules in CI
learn.microsoft.com
.
Consistent Style: Format your Bicep code for readability. Use two spaces for indentation (standard in Bicep). Align
property definitions in resource blocks, and use newline separation between resources and modules for clarity. Add comments to sections explaining complex logic (Bicep supports // comments). For long expressions, consider splitting them into multiple lines or variables. Make use of parameter and output descriptions (via the @description decorator) – this provides documentation within the template. Consistency is key: for example, if you use hyphens in resource names in one file, don’t switch to camelCase in another; keep the style uniform. Consider using a formatter (the VS Code Bicep extension formats on save) to automatically enforce spacing and line breaks.
Architecture and Structure
Modular Structure: Architect your Bicep templates in layers – for instance, have a foundation module (network, resource
groups, key vaults), a services module (app service plans, databases), and an app module (web apps, functions). The main Bicep file can orchestrate these modules, passing outputs from one to inputs of another. By isolating concerns, you can deploy or update parts of your infrastructure independently and promote reuse.
Dependencies and Outputs: Let Bicep handle dependencies implicitly by referencing resources via symbolic names instead
of using explicit dependsOn wherever possible. For example, if one resource needs the connection string of a storage account, have the storage account resource output the connection string, and pass it to the dependent resource’s properties (Bicep will infer the dependency). Avoid using the ARM reference() or manual resourceId construction when you can use symbolic references
learn.microsoft.com
 – e.g., use storageAccount.name or storageAccount.id directly if storageAccount is a symbolic name. This not only
 makes the code cleaner but also ensures correctness in dependency ordering. Use outputs in your modules and main file to expose important values (like resource IDs, keys, endpoint URLs) that other parts of the system or pipelines might need.
Parameterization & Environment Strategy: Use parameter files (.bicepparam or JSON parameter files) to deploy the same
Bicep with different settings per environment. For secret parameters (like admin passwords), do not hardcode them – either mark them as secure in Bicep and provide via secure pipeline variables or integrate with Key Vault (e.g., retrieve secret at deployment time via Key Vault reference). The linter will flag if you accidentally output a secret or have a secure parameter with an insecure default
learn.microsoft.com
 – heed these warnings. Consider using target scopes and nested deployments if you need to deploy to multiple scopes
 (like creating resource groups via Bicep requires deploying at the subscription scope). Plan your template structure such that each Bicep file has a clear responsibility and scope.
Modern Tooling
Use Latest API Versions: Always specify the most recent stable API version for each resource type (the Bicep VS Code
extension can often suggest this, or check Azure docs). New Azure features are only available in newer API versions, and using them ensures longevity of your template
learn.microsoft.com
. The linter can warn you if a resource is using a deprecated API version (enable rule use-recent-api-versions)
learn.microsoft.com
. Update your Bicep CLI regularly to take advantage of new language features (for example, loops, conditionals
improvements, extents support).
Integration with CI/CD: Integrate Bicep deployment in your pipelines. Use az deployment group create (or
New-AzResourceGroupDeployment in PowerShell) to deploy your bicep files as part of CI/CD, and use the --what-if (or New-AzResourceGroupDeployment -WhatIf) to preview changes – treat any unexpected resource deletions or modifications as warnings to be reviewed. You can also use GitHub Actions or Azure DevOps tasks specifically designed for Bicep. Additionally, consider using terraformer or AZ CLI export to initially scaffold Bicep from existing resources, then refine manually.
Testing and Validation: Besides using bicep build to validate syntax, use the Azure Resource Manager (ARM) What-If
feature or Bicep visualizer to ensure your changes are as expected. There are emerging tools for testing IaC (for example, Azure ARM TTK tests or Terratest with Bicep via ARM deployment) – incorporate those if your infrastructure code is critical. Also consider using Preflight/Checkov/tfsec-like tools (Checkov has some ARM/Bicep support) to scan for security issues (like open ports, weak TLS). Modern tooling around Bicep is growing, so keep an eye on the Bicep GitHub for linter rule updates and new features (like compile-time conditions, module registries, etc.) to continuously improve your Bicep projects.
Security, Testing, Performance, and DX
Security: Do not hardcode secrets (keys, passwords) in Bicep – use Azure Key Vault to store secrets and reference them
using the Key Vault reference syntax in your parameter files or link them at deployment time. Mark sensitive parameters as @secure() so that they are treated securely in Azure pipelines and not logged
learn.microsoft.com
. Implement role-based access control through your templates (e.g., use resource
Microsoft.Authorization/roleAssignments to assign appropriate roles to resources). Tag resources with ownership and environment tags so you have proper governance (some org policies might enforce certain tags; Bicep should include them to comply). If using public endpoints (like VMs with IPs or storage accounts), consider adding NSG rules or disabling public access where possible to reduce attack surface – these should be part of your template’s options (maybe behind a boolean parameter like allowPublicAccess).
Testing Deployments: Test your Bicep templates in a non-prod subscription or resource group before rolling out widely.
Use the what-if deployment mode to preview changes on existing infrastructure – this helps ensure your template updates won’t unintentionally replace or delete resources (for example, changing a resource name will show as a destroy/create in what-if). Incorporate these deployment tests into CI (you can have a nightly test deployment to a test RG and then teardown). After deployment, use PowerShell/CLI or Azure Resource Explorer to verify that all properties set by your Bicep (including tags, configuration settings) have taken effect correctly.
Performance and Limits: Be mindful of Azure limits – e.g., deploying too many resources at once (Bicep/ARM can throttle
or hit limits on template size or resource count). If your template is huge, break it into smaller modules and deploy in sequence or use orchestration (Azure DevOps pipelines or GitHub Actions can deploy step-by-step). Use deployment outputs instead of runtime lookups when chaining deployments (outputs are cached, whereas runtime reference() calls can slow down deployments). Where possible, prefer incremental deployments (the default) and ensure your template is idempotent – create or update resources but don’t delete unless intended. This avoids surprises in production.
Developer Experience: Keep your Bicep files readable and well-documented. At the top of files, include a comment header
describing what the template does. Use parameter descriptions to provide usage info. Leverage the VS Code Bicep extension’s visualizer to understand the resource graph – it’s a great way to review your architecture as code. If multiple team members work on IaC, establish a code review process for Bicep changes to catch mistakes (like accidentally removing a crucial setting). Generate documentation from your Bicep files using tools or scripts if needed (for example, parse the Bicep for parameters and outputs to produce a Markdown doc for reference). By treating Bicep as first-class code (with version control, reviews, and tests), you ensure your infrastructure is as reliable and maintainable as the applications running on it.
