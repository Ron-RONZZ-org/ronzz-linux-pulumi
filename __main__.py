"""Oracle Cloud Infrastructure Pulumi deployment for Linux server."""

import pulumi
import pulumi_oci as oci

# Get configuration
config = pulumi.Config()

# OCI Configuration - these should be set via pulumi config or environment variables
compartment_id = config.require("compartment_id")
availability_domain = config.require("availability_domain")
ssh_public_key = config.require("ssh_public_key")

# Optional configurations with defaults
subnet_id = config.get("subnet_id")
vcn_id = config.get("vcn_id")
image_id = config.get("image_id")

# If VCN and Subnet are not provided, create them
if not vcn_id:
    # Create Virtual Cloud Network (VCN)
    vcn = oci.core.Vcn(
        "ronzz-vcn",
        compartment_id=compartment_id,
        cidr_blocks=["10.0.0.0/16"],
        display_name="ronzz-vcn",
        dns_label="ronzz"
    )
    vcn_id = vcn.id

    # Create Internet Gateway
    internet_gateway = oci.core.InternetGateway(
        "ronzz-igw",
        compartment_id=compartment_id,
        vcn_id=vcn_id,
        enabled=True,
        display_name="ronzz-internet-gateway"
    )

    # Create Route Table
    route_table = oci.core.RouteTable(
        "ronzz-route-table",
        compartment_id=compartment_id,
        vcn_id=vcn_id,
        display_name="ronzz-route-table",
        route_rules=[
            oci.core.RouteTableRouteRuleArgs(
                network_entity_id=internet_gateway.id,
                destination="0.0.0.0/0",
                destination_type="CIDR_BLOCK"
            )
        ]
    )

    # Create Security List
    security_list = oci.core.SecurityList(
        "ronzz-security-list",
        compartment_id=compartment_id,
        vcn_id=vcn_id,
        display_name="ronzz-security-list",
        egress_security_rules=[
            oci.core.SecurityListEgressSecurityRuleArgs(
                destination="0.0.0.0/0",
                protocol="all",
                description="Allow all outbound traffic"
            )
        ],
        ingress_security_rules=[
            oci.core.SecurityListIngressSecurityRuleArgs(
                protocol="6",  # TCP
                source="0.0.0.0/0",
                description="Allow SSH",
                tcp_options=oci.core.SecurityListIngressSecurityRuleTcpOptionsArgs(
                    min=22,
                    max=22
                )
            ),
            oci.core.SecurityListIngressSecurityRuleArgs(
                protocol="1",  # ICMP
                source="0.0.0.0/0",
                description="Allow ICMP"
            )
        ]
    )

    # Create Subnet
    subnet = oci.core.Subnet(
        "ronzz-subnet",
        compartment_id=compartment_id,
        vcn_id=vcn_id,
        cidr_block="10.0.1.0/24",
        display_name="ronzz-subnet",
        dns_label="ronzzsubnet",
        route_table_id=route_table.id,
        security_list_ids=[security_list.id]
    )
    subnet_id = subnet.id

# If image_id is not provided, get the latest Oracle Linux image
if not image_id:
    # Get the latest Oracle Linux 8 image for ARM
    images = oci.core.get_images(
        compartment_id=compartment_id,
        operating_system="Oracle Linux",
        operating_system_version="8",
        shape="VM.Standard.A1",
        sort_by="TIMECREATED",
        sort_order="DESC"
    )
    if images.images:
        image_id = images.images[0].id
    else:
        # Fallback: let user specify or use a known image OCID
        raise Exception("No Oracle Linux 8 image found for VM.Standard.A1 shape. Please provide image_id via config.")

# Create Compute Instance (VM.Standard.A1 with 24GB RAM and 4 OCPUs)
instance = oci.core.Instance(
    "ronzz-linux-server",
    availability_domain=availability_domain,
    compartment_id=compartment_id,
    shape="VM.Standard.A1",
    shape_config=oci.core.InstanceShapeConfigArgs(
        ocpus=4,
        memory_in_gbs=24
    ),
    display_name="ronzz-linux-server",
    create_vnic_details=oci.core.InstanceCreateVnicDetailsArgs(
        subnet_id=subnet_id,
        assign_public_ip=True,
        display_name="ronzz-primary-vnic"
    ),
    source_details=oci.core.InstanceSourceDetailsArgs(
        source_type="image",
        image_id=image_id
    ),
    metadata={
        "ssh_authorized_keys": ssh_public_key
    }
)

# Get the public IP from the VNIC
vnic_attachments = oci.core.get_vnic_attachments_output(
    compartment_id=compartment_id,
    instance_id=instance.id
)

primary_vnic = oci.core.get_vnic_output(
    vnic_id=vnic_attachments.vnic_attachments[0].vnic_id
)

# Export the instance details
pulumi.export("instance_id", instance.id)
pulumi.export("instance_name", instance.display_name)
pulumi.export("instance_shape", instance.shape)
pulumi.export("public_ip", primary_vnic.public_ip_address)
pulumi.export("private_ip", primary_vnic.private_ip_address)
pulumi.export("instance_state", instance.state)
