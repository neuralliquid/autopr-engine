---
trigger: glob
globs: **/*.tf
---

Best Practices Code Organization: Structure Terraform code into logical modules. Use root module to
glue things together and create reusable modules for common patterns (e.g. VPC, database, server
group) rather than one giant configuration. This makes code easier to navigate and promotes reuse
across environments. Place related resources in the same file or folder, and use clear naming (e.g.
networking/vpc.tf, compute/instances.tf). Keep Terraform code DRY by using loops (count, for_each)
or modules instead of duplicating blocks. State Management: Use remote backend for Terraform state
(e.g. Azure Storage, S3 + DynamoDB lock, Terraform Cloud) instead of local state files, especially
in team environments. This ensures state is persisted, shared, and locked to prevent concurrent
runs. Protect the state (enable encryption at rest, use limited-access backend credentials) since it
may contain sensitive info. Use terraform workspaces or separate state files for isolating
environments (e.g. staging vs prod) rather than a single state for everything. Version Control &
Version Pinning: Commit your Terraform code and module code to version control. Pin provider
versions in the configuration (in required_providers) and Terraform version in required_version
developer.hashicorp.com using pessimistic constraints (like ~> 3.52 for AWS provider) to avoid
unexpected upgrades breaking your code. Do the same for module sources (if using public registry
modules, specify version = "x.y.z"). When upgrading Terraform or providers, review the release notes
for breaking changes. Linting and Formatting Terraform Fmt: Always run terraform fmt on your code
before check-in (or enable your editor to do so on save). This enforces the canonical style: 2-space
indents, consistent alignment of = signs, newlines between blocks, etc. developer.hashicorp.com
developer.hashicorp.com . Proper formatting makes diffs cleaner and the code easier to read for
everyone. Make it part of CI to reject improperly formatted code (the command can be run in check
mode). TFLint and Checkov: Use TFLint to catch common issues and enforce additional rules
developer.hashicorp.com . TFLint can warn about deprecated syntax, potential mistakes (like using
aws_instance without a key_name on AWS), and even policy checks. For security and compliance,
integrate Checkov or tfsec, which statically analyze Terraform for security risks (like open
security groups, unencrypted disks). These tools help maintain best practices beyond just style –
for example, they’ll flag if you accidentally leave an S3 bucket public. Style Guide Conventions:
Adhere to a consistent style in naming and structure: use lowercase with underscores for resource
names and Terraform variables (e.g. resource "aws_instance" "app_server" – the resource name
app_server is lowercase and underscores) developer.hashicorp.com . Do not include the provider or
type in the resource name (since the resource block already indicates the type)
developer.hashicorp.com . Name Terraform variables clearly (e.g. instance_count instead of count to
avoid shadowing). Provide descriptions for variables and outputs for clarity developer.hashicorp.com
. Group related configuration – for instance, keep all variables in a variables.tf and outputs in
outputs.tf to standardize layout. Keeping a tidy and convention-driven repo makes it easier for
contributors to find things and understand the configuration. Architecture and Structure Logical
Separation: Separate different concerns into different Terraform configurations or workspaces. For
example, manage core infrastructure (network, IAM) in one config and application-specific
infrastructure in another, if they have different lifecycles. This prevents accidental changes to
core infra when deploying apps. Use Terraform workspaces or separate state files to isolate stages
(dev/staging/prod) – don't use a single state for all environments, to avoid cross-impact. Module
Usage: Use modules for grouping resources that form a logical unit (e.g., a module for a web service
that includes an autoscaling group, load balancer, and associated security groups). Define module
inputs and outputs clearly so that the module is black-box reusable. For internal modules, version
them (even if just via Git SHA or a registry) so changes are tracked. Within modules, follow
standard structure: main.tf, variables.tf, outputs.tf for clarity. Modules not only promote reuse
but also make large configs more manageable by abstracting details. State and Dependency Management:
Be mindful of implicit dependencies. Terraform generally figures out resource order by references,
but in cases where it cannot (or to make it explicit), use depends_on. However, prefer using outputs
and interpolations to create implicit dependencies rather than adding many manual depends_on. Avoid
data races like one resource reading data from another resource’s API (use Terraform data sources
carefully and understand that could cause refresh cycles). If using remote data (data sources), know
that if those resources change out of band, Terraform might not notice unless you refresh. For
critical external dependencies, consider importing them as managed resources (if you’re allowed) or
have documentation on how they’re managed. Modern Tooling Terraform Version and Features: Keep up
with Terraform improvements. Terraform 1.x has added features like preconditions/postconditions for
resource validation spacelift.io spacelift.io and the import block for importing existing resources
into state. Use these features to your advantage – e.g., add a precondition to ensure a variable
meets some criteria (like Azure location is within allowed list) to catch errors early. Use moved
blocks (in 1.x) to refactor/rename resources without destroying them. Keep Terraform updated to a
stable recent release to get bug fixes and enhancements (but avoid cutting-edge releases in prod
without testing). Tooling Ecosystem: Consider using tools like Terragrunt if you have many
environments and want to reduce code duplication – Terragrunt can generate Terraform config from
live directories and manage backend configs per env. If you prefer not to introduce Terragrunt,
ensure your own structure is DRY (perhaps use partial configurations or scripts to generate configs
for similar envs). Utilize terraform validate in CI to catch errors before apply
developer.hashicorp.com . Use tfsec/Checkov (as mentioned) in pipelines to enforce security. For
complex changes, terraform’s plan output can be hard to read – consider using the human-readable
diff tools or the JSON plan output with automation to detect significant changes (there are
community tools that comment on PRs with plan summaries). State Insights and Backup: Use terraform
show and terraform state list to inspect state when needed. Regularly backup your state (if remote,
ensure the storage has versioning). Should something go wrong (e.g., state corruption or accidental
resource deletion in cloud), having backups and understanding of state can be a lifesaver. Modern
backends (Terraform Cloud, etc.) have state history – leverage that if available. Also, use the
state locking mechanism (most backends have it) – it prevents concurrent runs which could corrupt
state. If you integrate with CI, configure it such that only one apply can run at a time against a
given state (or use Terraform Cloud/Enterprise which handles a queue). Security, Testing,
Performance, and DX Security: Never commit secrets into Terraform files or variable files. Use
Terraform’s sensitive variables for things like passwords or keys (marking output as sensitive =
true to avoid printing to console) developer.hashicorp.com . Leverage cloud provider’s secret stores
(AWS Secrets Manager, Azure Key Vault) by retrieving secrets at runtime via data sources or
integrating with provisioning (better than having them in plaintext in TF vars). Implement
guardrails: for example, if deploying security groups, default to least privilege (no wide-open
0.0.0.0/0 unless explicitly intended). If possible, run terraform plan/apply in a controlled
environment (CI) with restricted credentials that only have access to needed resources – this
reduces blast radius if the credentials are compromised. Testing Infrastructure as Code: While
Terraform doesn’t have a built-in testing framework, you can implement testing by writing scripts
that do terraform plan and parse the output for unexpected changes. Consider using Terratest (a Go
library) to programmatically deploy a Terraform stack to a test environment and then assert on the
infrastructure (for example, check if an AWS EC2 instance is actually running via AWS SDK). At
minimum, always do a manual review of the terraform plan output before applying in production and
possibly have a peer review it as well (e.g., require approval on a pull request that includes the
plan output). This human-in-the-loop catches mistakes that automated lint might not (like
accidentally destroying a DB instance). Performance: Terraform’s performance mostly concerns how
quickly it can plan and apply. Keep the number of resources in a single state reasonable – thousands
of resources in one plan can slow down operations and increase the chance of timeouts. If you hit
performance issues, break configurations into modules or separate states. Use the -parallelism flag
(with care) to increase concurrent resource provisioning if your environment can handle it – by
default Terraform applies up to 10 resources in parallel. Ensure you’re not doing superfluous work:
e.g., avoid null_resource and local-exec hacks that run every apply unless absolutely needed (they
can be slow and often there are better IaC-native ways). Developer Experience: Make it easy to work
with Terraform for your team. Provide README documentation for each module explaining inputs/outputs
and usage. Use descriptive variable names and defaults that make sense (and mention units/currency
in the var description if relevant). When someone new looks at the code, clear structure and
comments help them ramp up. Use consistent ordering in resource blocks (Terraform fmt does some of
this) – e.g., first provider, then resource type and name, then properties with tags last – small
consistency touches reduce cognitive load. If you leverage IDE tools (VS Code Terraform extension,
JetBrains HCL plugin), those can provide completion and highlight errors as you type – encourage
their use. Finally, treat Terraform code reviews like application code reviews: check for
correctness, clarity, and adherence to best practices. This fosters a culture where infrastructure
is code, subject to the same quality controls as application code.
