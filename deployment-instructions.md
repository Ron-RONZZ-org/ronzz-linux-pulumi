# Deployment Instructions for Oracle Cloud Linux Server

This guide provides step-by-step instructions for deploying an Oracle Cloud Infrastructure (OCI) Linux server using Pulumi.

## Infrastructure Overview

This Pulumi project deploys the following resources:

- **Compute Instance**: VM.Standard.A1 (ARM-based)
  - 4 OCPUs (Oracle CPUs)
  - 24 GB RAM
  - Oracle Linux 8 (latest image)
- **Networking** (created automatically if not provided):
  - Virtual Cloud Network (VCN)
  - Internet Gateway
  - Route Table
  - Security List (allows SSH and ICMP)
  - Subnet

## Prerequisites

Before you begin, ensure you have the following:

1. **Oracle Cloud Account**: Active OCI account with appropriate permissions
2. **Pulumi CLI**: Version 3.0 or higher
3. **Python**: Version 3.7 or higher
4. **OCI CLI** (optional but recommended): For easier configuration
5. **SSH Key Pair**: For accessing the compute instance

## Setup Instructions

### 1. Install Dependencies

Clone the repository and install Python dependencies:

```bash
cd ronzz-linux-pulumi
pip install -r requirements.txt
```

Or use a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure OCI Credentials

You need to configure OCI authentication. There are two methods:

#### Method A: Using OCI CLI Configuration (Recommended)

1. Install OCI CLI: https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm
2. Configure OCI CLI:
   ```bash
   oci setup config
   ```
3. Set environment variables:
   ```bash
   export OCI_CLI_CONFIG_FILE=~/.oci/config
   export OCI_CLI_PROFILE=DEFAULT
   ```

#### Method B: Using Environment Variables

Set the following environment variables:

```bash
export OCI_TENANCY_OCID=<your-tenancy-ocid>
export OCI_USER_OCID=<your-user-ocid>
export OCI_FINGERPRINT=<your-api-key-fingerprint>
export OCI_PRIVATE_KEY_PATH=<path-to-your-private-key>
export OCI_REGION=<your-region>
```

### 3. Initialize Pulumi Stack

Initialize a new Pulumi stack (or use an existing one):

```bash
pulumi login  # Login to Pulumi (you can use local backend: pulumi login --local)
pulumi stack init dev  # Create a new stack named 'dev'
```

### 4. Configure Required Parameters

Set the required configuration values for your deployment:

```bash
# Required configurations
pulumi config set compartment_id <your-compartment-ocid>
pulumi config set availability_domain <your-availability-domain>
pulumi config set ssh_public_key "<your-ssh-public-key-content>"
```

**Finding Your Values:**

- **Compartment OCID**: Go to OCI Console → Identity & Security → Compartments
- **Availability Domain**: Format is usually `<region>-AD-1`, `<region>-AD-2`, etc.
  - Example: `US-ASHBURN-AD-1`
  - You can list them using: `oci iam availability-domain list`
- **SSH Public Key**: Content of your `~/.ssh/id_rsa.pub` file

**Optional configurations** (if you have existing network resources):

```bash
pulumi config set vcn_id <existing-vcn-ocid>
pulumi config set subnet_id <existing-subnet-ocid>
pulumi config set image_id <specific-image-ocid>
```

### 5. Preview the Deployment

Before deploying, preview the changes:

```bash
pulumi preview
```

This will show you all the resources that will be created.

### 6. Deploy the Infrastructure

Deploy the infrastructure:

```bash
pulumi up
```

Review the changes and confirm by typing "yes" when prompted.

The deployment typically takes 3-5 minutes. Upon completion, you'll see output similar to:

```
Outputs:
    instance_id    : "ocid1.instance.oc1..."
    instance_name  : "ronzz-linux-server"
    instance_shape : "VM.Standard.A1"
    private_ip     : "10.0.1.2"
    public_ip      : "123.45.67.89"
    instance_state : "RUNNING"
```

### 7. Access Your Server

Once deployed, connect to your server via SSH:

```bash
ssh opc@<public_ip>
```

The default username for Oracle Linux is `opc`.

## Managing Your Infrastructure

### View Current State

```bash
pulumi stack output  # View all outputs
pulumi stack output public_ip  # View specific output
```

### Update Configuration

To change instance configuration:

```bash
# Example: Update SSH key
pulumi config set ssh_public_key "<new-public-key>"
pulumi up
```

### Destroy Infrastructure

To destroy all resources:

```bash
pulumi destroy
```

Review the resources to be deleted and confirm by typing "yes".

## Troubleshooting

### Image Not Found Error

If you get an error about image not found:

1. Manually find an Oracle Linux 8 image OCID for VM.Standard.A1:
   ```bash
   oci compute image list \
     --compartment-id <your-compartment-ocid> \
     --operating-system "Oracle Linux" \
     --shape "VM.Standard.A1"
   ```

2. Set it in the config:
   ```bash
   pulumi config set image_id <image-ocid>
   ```

### Service Limits

VM.Standard.A1 instances use ARM-based processors and are part of Oracle's Always Free tier (limited resources). Ensure you have:

- Available compute instances in your service limits
- Available OCPUs for the A1 shape (4 OCPUs required)
- Available memory (24 GB required)

Check service limits in OCI Console → Governance & Administration → Limits, Quotas and Usage

### SSH Connection Issues

If you cannot connect via SSH:

1. Verify security list allows port 22 from your IP
2. Check the instance is in "RUNNING" state
3. Verify your SSH key was correctly configured
4. Check you're using the correct username (`opc` for Oracle Linux)

## Cost Considerations

- **VM.Standard.A1**: Oracle Cloud offers Always Free tier with up to 4 OCPUs and 24 GB RAM across A1 instances
- **Network**: Outbound data transfer may incur charges beyond free tier limits
- **Storage**: Boot volume storage (default 50GB) is included

Always monitor your usage in the OCI Console to avoid unexpected charges.

## Security Best Practices

1. **SSH Keys**: Never commit private keys to version control
2. **Security Lists**: Restrict SSH access to specific IP addresses instead of 0.0.0.0/0
3. **Updates**: Keep your OS and packages updated:
   ```bash
   sudo dnf update -y
   ```
4. **Firewall**: Configure local firewall rules as needed
5. **API Keys**: Rotate OCI API keys regularly

## Additional Resources

- [Pulumi OCI Documentation](https://www.pulumi.com/registry/packages/oci/)
- [Oracle Cloud Infrastructure Documentation](https://docs.oracle.com/en-us/iaas/Content/home.htm)
- [VM.Standard.A1 Shape Information](https://docs.oracle.com/en-us/iaas/Content/Compute/References/arm.htm)
- [Pulumi Documentation](https://www.pulumi.com/docs/)

## Support

For issues with:
- **Pulumi**: Check [Pulumi Community Slack](https://slack.pulumi.com/)
- **OCI**: Contact Oracle Cloud Support
- **This Project**: Open an issue in the GitHub repository
