# ronzz-linux-pulumi

Infrastructure as Code for deploying Oracle Cloud Linux server using Pulumi.

## Overview

This repository contains Pulumi infrastructure code to deploy computing resources on Oracle Cloud Infrastructure (OCI):

- **Compute Instance**: VM.Standard.A1 (ARM-based processor)
  - 4 OCPUs
  - 24 GB RAM
  - Oracle Linux 8

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure OCI credentials (see [deployment-instructions.md](deployment-instructions.md))

3. Set required configuration:
   ```bash
   pulumi config set compartment_id <your-compartment-ocid>
   pulumi config set availability_domain <your-availability-domain>
   pulumi config set ssh_public_key "<your-ssh-public-key>"
   ```

4. (Optional) Set image selection

   The deployment accepts an `image_id` configuration which can be either:

   - A full OCI image OCID (recommended), for example `ocid1.image...`
   - A display name of an image (the script will attempt to resolve it to an OCID)

   Examples:

   ```bash
   # Recommended: provide the image OCID directly
   pulumi config set image_id ocid1.image.oc1..aaaaaaaaxxxxx

   # Or provide a display_name (the script will try to resolve it)
   pulumi config set image_id "Canonical-Ubuntu-24.04-Minimal-aarch64-2025.10.31-0"
   ```

4. Deploy:
   ```bash
   pulumi up
   ```

## Documentation

For detailed deployment instructions, troubleshooting, and configuration options, see [deployment-instructions.md](deployment-instructions.md).

## Resources Created

- Virtual Cloud Network (VCN) with CIDR 10.0.0.0/16
- Internet Gateway for public connectivity
- Route Table and Security List (SSH and ICMP enabled)
- Subnet (10.0.1.0/24)
- Compute Instance (VM.Standard.A1 with 4 OCPUs and 24GB RAM)

## Requirements

- Pulumi CLI (v3.0+)
- Python 3.7+
- Oracle Cloud Infrastructure account
- SSH key pair

Notes:
- If you provide a display name rather than an OCID, the Pulumi code will:
   1. Try to find an image with that exact `display_name` in the configured compartment.
   2. If not found, fall back to searching recent Canonical Ubuntu 24.04 images and match by substring.
   3. If still not found, the deployment will fail and ask you to provide a valid OCID.

- For predictable results across regions and tenancy boundaries, prefer supplying the image OCID shown in the OCI Console.
