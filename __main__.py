"""Oracle Cloud Infrastructure Pulumi deployment for Linux server."""

import pulumi
import pulumi_oci as oci

# Use pulumi logging so messages show up during `pulumi up` / `pulumi preview`
log = pulumi.log

# Get configuration
config = pulumi.Config()

# OCI Configuration - these should be set via pulumi config or environment variables
compartment_id = config.require("compartment_id")
availability_domain = config.require("availability_domain")
ssh_public_key = config.require("ssh_public_key")

# Optional configurations with defaults
subnet_id = config.get("subnet_id")
vcn_id = config.get("vcn_id")
image_id_config = config.get(
    "image_id"
)  # Keep config separate to avoid Output confusion

# If VCN and Subnet are not provided, create them
if not vcn_id:
    # Create Virtual Cloud Network (VCN)
    vcn = oci.core.Vcn(
        "ronzz-vcn",
        compartment_id=compartment_id,
        cidr_blocks=["10.0.0.0/16"],
        display_name="ronzz-vcn",
        dns_label="ronzz",
    )
    vcn_id = vcn.id

    # Create Internet Gateway
    internet_gateway = oci.core.InternetGateway(
        "ronzz-igw",
        compartment_id=compartment_id,
        vcn_id=vcn_id,
        enabled=True,
        display_name="ronzz-internet-gateway",
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
                destination_type="CIDR_BLOCK",
            )
        ],
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
                description="Allow all outbound traffic",
            )
        ],
        ingress_security_rules=[
            oci.core.SecurityListIngressSecurityRuleArgs(
                protocol="6",  # TCP
                source="0.0.0.0/0",
                description="Allow SSH",
                tcp_options=oci.core.SecurityListIngressSecurityRuleTcpOptionsArgs(
                    min=22, max=22
                ),
            ),
            oci.core.SecurityListIngressSecurityRuleArgs(
                protocol="1", source="0.0.0.0/0", description="Allow ICMP"  # ICMP
            ),
        ],
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
        security_list_ids=[security_list.id],
    )
    subnet_id = subnet.id

# Determine the image OCID to use
# We need to ensure this is a plain string OCID, not a Pulumi Output,
# to avoid "CannotParseRequest" errors when creating the instance.
resolved_image_id = None

# If image_id is not provided, get the latest Ubuntu Linux image
if not image_id_config:
    # Get the latest Ubuntu Linux 24.04 image for ARM flexible shapes
    images = oci.core.get_images(
        compartment_id=compartment_id,
        operating_system="Canonical Ubuntu",
        operating_system_version="24.04",
        shape="VM.Standard.A1.Flex",
        sort_by="TIMECREATED",
        sort_order="DESC",
    )
    if images.images:
        resolved_image_id = images.images[0].id
        log.info(
            f"Auto-selected image {images.images[0].display_name} (OCID: {resolved_image_id})"
        )
    else:
        # Fallback: let user specify or use a known image OCID
        raise Exception(
            "No Ubuntu Linux 24.04 image found for VM.Standard.A1.Flex shape. Please provide image_id via config."
        )

# Validate provided image_id (if user supplied one) to ensure it's valid in the region.
# If the user supplied a display name (not an OCID), try to resolve it to an OCID by
# searching images by display_name or by matching recent Ubuntu images.
if image_id_config:
    # If it looks like an OCID for an image, validate directly.
    if isinstance(image_id_config, str) and image_id_config.startswith("ocid1.image"):
        try:
            log.info(f"Validating provided image OCID: {image_id_config}")
            _ = oci.core.get_image(image_id=image_id_config)
            log.info("Image OCID validated successfully.")
            resolved_image_id = image_id_config
        except Exception as e:
            raise Exception(
                f"Provided image_id '{image_id_config}' is not valid in this region or cannot be found: {e}"
            )
    else:
        # Treat the provided value as a display_name and attempt to resolve it.
        try:
            log.info(
                f"Attempting to resolve image display_name '{image_id_config}' in compartment {compartment_id}"
            )
            images = oci.core.get_images(
                compartment_id=compartment_id,
                display_name=image_id_config,
            )
            if images and getattr(images, "images", None):
                # Use the first exact match
                selected = images.images[0]
                resolved_image_id = selected.id
                log.info(
                    f"Resolved display_name to image {selected.display_name} (OCID: {resolved_image_id})"
                )
            else:
                # Fallback: try to find a recent Ubuntu 24.04 image and match by substring
                log.info(
                    "No exact display_name match found; searching recent Canonical Ubuntu 24.04 images as fallback"
                )
                images = oci.core.get_images(
                    compartment_id=compartment_id,
                    operating_system="Canonical Ubuntu",
                    operating_system_version="24.04",
                    shape="VM.Standard.A1.Flex",
                    sort_by="TIMECREATED",
                    sort_order="DESC",
                )
                match = None
                for img in getattr(images, "images", []) or []:
                    # exact match first, then substring
                    if getattr(img, "display_name", None) == image_id_config:
                        match = img
                        break
                    if image_id_config in getattr(img, "display_name", ""):
                        match = img
                        break

                if match:
                    resolved_image_id = match.id
                    log.info(
                        f"Fallback resolved display_name to image {match.display_name} (OCID: {resolved_image_id})"
                    )
                else:
                    raise Exception(
                        "Provided image identifier does not look like an OCID and could not be resolved to an image OCID in this compartment/region.\n"
                        "Please provide a valid image OCID (starts with 'ocid1.image') or a display_name that exists in this tenancy/compartment.\n"
                        f"Provided value: '{image_id_config}'"
                    )
        except Exception as e:
            # Re-raise with clearer context
            raise Exception(
                f"Failed to resolve provided image identifier '{image_id_config}' to a valid image OCID: {e}"
            )

# Ensure we have a resolved image ID before proceeding
if not resolved_image_id:
    raise Exception(
        "No image ID could be determined. Please provide image_id via config or ensure compatible images exist in your compartment."
    )

# If a subnet was provided, validate that the availability domain matches the subnet (if subnet is AD-scoped)
if subnet_id:
    try:
        subnet_info = oci.core.get_subnet(subnet_id=subnet_id)
        subnet_ad = getattr(subnet_info, "availability_domain", None)
        # Some subnets are regional and do not have an availability_domain attribute; only validate when present
        if subnet_ad and subnet_ad != availability_domain:
            raise Exception(
                f"Provided availability_domain '{availability_domain}' does not match subnet's availability_domain '{subnet_ad}'."
            )
    except Exception as e:
        raise Exception(f"Failed to validate subnet '{subnet_id}': {e}")

# Create Compute Instance using A1 Flex with explicit shape_config (ocpus and memory)
instance = oci.core.Instance(
    "ronzz-linux-server",
    availability_domain=availability_domain,
    compartment_id=compartment_id,
    # Use the flexible ARM shape
    shape="VM.Standard.A1.Flex",
    # Provide shape_config for flexible shapes (use camelCase property names)
    shape_config=oci.core.InstanceShapeConfigArgs(ocpus=1.0, memory_in_gbs=6.0),
    display_name="ronzz-linux-server",
    create_vnic_details=oci.core.InstanceCreateVnicDetailsArgs(
        subnet_id=subnet_id, assign_public_ip=True, display_name="ronzz-primary-vnic"
    ),
    source_details=oci.core.InstanceSourceDetailsArgs(
        source_type="image", source_id=resolved_image_id
    ),
    metadata={
        "ssh_authorized_keys": ssh_public_key,
    },
    # Removed invalid/unsupported instance_type parameter
    is_pv_encryption_in_transit_enabled=True,
)


# Get the public IP from the VNIC
def get_vnic_details(instance_id):
    vnic_attachments = oci.core.get_vnic_attachments(
        compartment_id=compartment_id, instance_id=instance_id
    )
    if vnic_attachments.vnic_attachments:
        vnic_id = vnic_attachments.vnic_attachments[0].vnic_id
        primary_vnic = oci.core.get_vnic(vnic_id=vnic_id)
        return primary_vnic
    return None


# Use apply to handle the async operations
primary_vnic_output = instance.id.apply(get_vnic_details)

# Export the instance details
pulumi.export("instance_id", instance.id)
pulumi.export("instance_name", instance.display_name)
pulumi.export("instance_shape", instance.shape)
pulumi.export(
    "public_ip",
    primary_vnic_output.apply(lambda vnic: vnic.public_ip_address if vnic else "N/A"),
)
pulumi.export(
    "private_ip",
    primary_vnic_output.apply(lambda vnic: vnic.private_ip_address if vnic else "N/A"),
)
pulumi.export("instance_state", instance.state)
