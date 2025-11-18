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
