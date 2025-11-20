# Copilot Instructions for ronzz-linux-pulumi

## Repository Overview

This repository contains Pulumi Infrastructure as Code (IaC) for deploying Oracle Cloud Infrastructure (OCI) resources, specifically:
- **Purpose**: Deploy and manage Oracle Cloud Linux servers using Pulumi and Python
- **Primary Cloud Provider**: Oracle Cloud Infrastructure (OCI)
- **Infrastructure Tool**: Pulumi (Python runtime)
- **Main Resources**: VCN, Subnets, Security Lists, Route Tables, and Compute Instances (VM.Standard.A1)

## Technology Stack

- **Language**: Python 3.12+
- **IaC Framework**: Pulumi v3.0+
- **Cloud SDK**: pulumi-oci v2.0+
- **Package Manager**: Poetry (configured via pyproject.toml)
- **Compute Shape**: VM.Standard.A1 (ARM-based, 4 OCPUs, 24GB RAM)
- **Operating System**: Oracle Linux 8 / Ubuntu Linux 24.04

## Code Structure

- `__main__.py`: Main Pulumi infrastructure definition
- `Pulumi.yaml`: Pulumi project configuration
- `pyproject.toml`: Python project dependencies and metadata
- `requirements.txt`: Python dependencies for deployment
- `deployment-instructions.md`: Detailed deployment and configuration guide

## Coding Guidelines

### Python Style
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Use descriptive variable names (e.g., `compartment_id`, `availability_domain`)
- Keep functions focused and modular
- Add docstrings for complex functions

### Pulumi Best Practices
- **Resource Naming**: Use descriptive resource names prefixed with "ronzz-" (e.g., "ronzz-vcn", "ronzz-subnet")
- **Configuration Management**: Use `pulumi.Config()` for all configurable values
- **Required vs Optional**: Mark essential configs with `.require()`, optional with `.get()`
- **Exports**: Export important resource details (instance_id, public_ip, private_ip, etc.)
- **Dependencies**: Let Pulumi handle implicit dependencies via resource references
- **Async Operations**: Use `.apply()` for operations that depend on resource outputs

### OCI-Specific Guidelines
- **Compartment ID**: Always require compartment_id via configuration
- **Availability Domain**: Always require availability_domain via configuration
- **Network Security**: Follow principle of least privilege for Security Lists
- **Resource Tagging**: Use display_name for all resources for better visibility in OCI Console
- **DNS Labels**: Use alphanumeric DNS labels without hyphens (e.g., "ronzz", "ronzzsubnet")

## Development Workflow

### Setup
1. Ensure Python 3.12+ is installed
2. Install dependencies: `pip install -r requirements.txt` or use Poetry
3. Configure OCI credentials (see deployment-instructions.md)
4. Set Pulumi configuration values before deployment

### Making Changes
1. **Test Locally**: Use `pulumi preview` to see planned changes before applying
2. **Incremental Updates**: Make small, focused changes to infrastructure
3. **Validate Syntax**: Run `python __main__.py` to check for syntax errors
4. **Preview Changes**: Always run `pulumi preview` before `pulumi up`
5. **Apply Changes**: Use `pulumi up` to deploy infrastructure changes

### Testing and Validation
- **Syntax Check**: `python -m py_compile __main__.py`
- **Pulumi Preview**: `pulumi preview` (dry-run to see what will change)
- **Pulumi Validation**: Check for configuration errors and resource conflicts
- **Post-Deployment**: Verify resources in OCI Console and test SSH connectivity

## Important Configuration Values

The following configuration values must be set before deployment:
- `compartment_id`: OCI compartment OCID (required)
- `availability_domain`: OCI availability domain (required)
- `ssh_public_key`: SSH public key for instance access (required)

Optional configuration values:
- `subnet_id`: Use existing subnet (if not provided, a new one is created)
- `vcn_id`: Use existing VCN (if not provided, a new one is created)
- `image_id`: Specific image OCID (if not provided, latest Ubuntu 24.04 is used)

## Common Tasks

### Adding New Resources
1. Follow existing naming conventions (prefix with "ronzz-")
2. Add display_name for visibility in OCI Console
3. Use pulumi.Config() for configurable parameters
4. Export important resource attributes
5. Run `pulumi preview` to validate changes

### Modifying Network Configuration
1. Update Security List rules in the `ingress_security_rules` or `egress_security_rules` lists
2. Modify CIDR blocks in VCN or Subnet definitions
3. Add new Route Table rules for routing changes
4. Always preview changes before applying to avoid network disruptions

### Updating Compute Instance
1. Changes to `shape`, `image_id`, or `metadata` may require instance replacement
2. Use `pulumi up` with caution as it may cause downtime
3. Consider using Pulumi's `protect` option for critical resources
4. Backup data before making destructive changes

## Security Considerations

- **SSH Keys**: Never commit private keys or sensitive credentials to the repository
- **Secrets Management**: Use Pulumi secrets for sensitive configuration values: `pulumi config set --secret`
- **Network Access**: Restrict SSH access (port 22) to known IP ranges when possible
- **Encryption**: Use `is_pv_encryption_in_transit_enabled=True` for data encryption
- **Least Privilege**: Only open necessary ports in Security Lists

## Troubleshooting

### Common Issues
1. **Image Not Found**: Specify `image_id` explicitly if automatic detection fails
2. **Capacity Issues**: VM.Standard.A1 shapes may have limited availability in some regions
3. **Configuration Errors**: Verify all required config values are set with `pulumi config`
4. **Authentication**: Ensure OCI credentials are properly configured (see deployment-instructions.md)

### Debug Steps
1. Check Pulumi logs: `pulumi logs`
2. Verify OCI credentials: `oci iam region list`
3. Review resource state: `pulumi stack`
4. Check for drift: `pulumi refresh`

## Additional Resources

- [Pulumi Python Documentation](https://www.pulumi.com/docs/languages-sdks/python/)
- [Pulumi OCI Provider Documentation](https://www.pulumi.com/registry/packages/oci/)
- [Oracle Cloud Infrastructure Documentation](https://docs.oracle.com/en-us/iaas/Content/home.htm)
- Repository deployment guide: `deployment-instructions.md`
