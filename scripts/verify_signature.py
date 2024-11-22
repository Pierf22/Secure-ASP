import argparse
import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature


# Function to read and load the public key from a file
def load_public_key(public_key_file):
    with open(public_key_file, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())
    return public_key


# Function to load the signature from PEM format
def load_signature_from_pem(signature_file):
    with open(signature_file, "r") as f:
        pem_signature = f.read()

    # Remove the PEM headers and footers, then decode the Base64
    signature_b64 = (
        pem_signature.replace("-----BEGIN SIGNATURE-----", "")
        .replace("-----END SIGNATURE-----", "")
        .strip()
    )
    signature = base64.b64decode(signature_b64)
    return signature


# Function to verify the signature of a file with the public key
def verify_signature(public_key, file_to_verify, signature):
    # Read the file data
    with open(file_to_verify, "rb") as f:
        file_data = f.read()

    try:
        # Verify the signature
        public_key.verify(
            signature,
            file_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )
        print("Signature is valid.")
    except InvalidSignature:
        print("Signature is invalid.")


# Main function
def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(
        description="Verify the signature of a file using a public key."
    )
    parser.add_argument(
        "public_key_file", help="Path to the public key file (PEM format)"
    )
    parser.add_argument("file_to_verify", help="Path to the original file to verify")
    parser.add_argument(
        "signature_file", help="Path to the signature of the file (PEM format)"
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    # Load the public key
    public_key = load_public_key(args.public_key_file)

    # Load the signature
    signature = load_signature_from_pem(args.signature_file)

    # Verify the signature
    verify_signature(public_key, args.file_to_verify, signature)


# Entry point of the script
if __name__ == "__main__":
    main()
