import argparse
import os
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64


# Function to read and load the private key from a file
def load_private_key(private_key_file):
    with open(private_key_file, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)
    return private_key


# Function to sign a file with the private key
def sign_file(private_key, file_to_sign):
    # Read the file data
    with open(file_to_sign, "rb") as f:
        file_data = f.read()

    # Sign the file data
    signature = private_key.sign(
        file_data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256(),
    )
    return signature


# Function to convert signature to PEM format
def signature_to_pem(signature):
    # Encode the signature in Base64
    signature_b64 = base64.b64encode(signature).decode("utf-8")

    # Format it with PEM headers and footers
    pem_signature = (
        "-----BEGIN SIGNATURE-----\n"
        + "\n".join(signature_b64[i : i + 64] for i in range(0, len(signature_b64), 64))
        + "\n-----END SIGNATURE-----\n"
    )
    return pem_signature


# Function to generate a .sign file name based on the input file without its extension
def generate_sign_file_name(file_to_sign):
    base_name = os.path.splitext(os.path.basename(file_to_sign))[
        0
    ]  # Remove the extension
    sign_file_name = base_name + ".sign"  # Append ".sign" to the base name
    return sign_file_name


# Main function
def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(
        description="Read, load a private key, and sign a file."
    )
    parser.add_argument(
        "private_key_file", help="Path to the private key file (PEM format)"
    )
    parser.add_argument("file_to_sign", help="Path to the file to be signed")
    parser.add_argument(
        "-d", "--directory", default=".", help="Directory to save the signature file (default: current directory)"
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    # Generate the .sign file name based on the input file
    sign_file_name = generate_sign_file_name(args.file_to_sign)

    # Ensure the directory exists
    if not os.path.exists(args.directory):
        os.makedirs(args.directory)

    # Create the full path for the signature file
    output_signature_file = os.path.join(args.directory, sign_file_name)

    # Read and load the private key
    private_key = load_private_key(args.private_key_file)

    # Sign the file
    signature = sign_file(private_key, args.file_to_sign)

    # Convert the signature to PEM format
    pem_signature = signature_to_pem(signature)

    # Save the signature in PEM format to a file
    with open(output_signature_file, "w") as sig_file:
        sig_file.write(pem_signature)

    print(f"File successfully signed. Signature saved to {output_signature_file}")

# Entry point of the script
if __name__ == "__main__":
    main()
