import os
import argparse
from cryptography import x509
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


# Function to read and load the private key from a file
def load_private_key(private_key_file):
    with open(private_key_file, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)
    return private_key


# Function to generate a CSR using the provided private key
def generate_csr(private_key):
    csr = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(
            x509.Name(
                [
                    x509.NameAttribute(
                        NameOID.COUNTRY_NAME, "IT"
                    ),  # Change country code to IT (Italy)
                    x509.NameAttribute(
                        NameOID.STATE_OR_PROVINCE_NAME, "Calabria"
                    ),  # Use Calabria as in generate_certificate
                    x509.NameAttribute(
                        NameOID.LOCALITY_NAME, "Rende"
                    ),  # City from generate_certificate
                    x509.NameAttribute(
                        NameOID.ORGANIZATION_NAME, "Secure ASP"
                    ),  # Organization name
                ]
            )
        )
        .add_extension(
            x509.SubjectAlternativeName(
                [
                    x509.DNSName("secureasp.com"),  # Primary domain name
                ]
            ),
            critical=False,
        )
        .sign(private_key, hashes.SHA256())
    )  # Sign the CSR using the private key

    # Serialize the CSR to PEM format and return it as a string
    csr_pem = csr.public_bytes(serialization.Encoding.PEM).decode("utf-8")
    return csr_pem




# Main function
def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(
        description="Read and load a private key from a file and generate a CSR."
    )
    parser.add_argument(
        "private_key_file", help="Path to the private key file (PEM format)"
    )
    parser.add_argument(
        "-d", "--directory", default=".", help="Directory to save the generated CSR (default: current directory)"
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    # Read and load the private key
    private_key = load_private_key(args.private_key_file)

    # Print confirmation and display the private key
    print("Private key successfully loaded.")
    print(private_key)

    # Generate the CSR (Certificate Signing Request)
    csr_pem = generate_csr(private_key)

    # Ensure the directory exists
    if not os.path.exists(args.directory):
        os.makedirs(args.directory)

    # Construct the output file path (using fixed filename 'csr_request.pem')
    output_file = os.path.join(args.directory, "csr_request.pem")
    
    # Write the CSR to the file
    with open(output_file, "w") as f:
        f.write(csr_pem)  # Write CSR as text, not in binary mode

    print(f"CSR successfully generated and saved to {output_file}")


# Entry point of the script
if __name__ == "__main__":
    main()

