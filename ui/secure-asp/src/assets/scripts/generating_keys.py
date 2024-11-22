import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import argparse

# Function to generate RSA key pair (private and public)
def generate_rsa_keypair():
    # Generate a 2048-bit RSA private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    return private_key


# Function to save the private key to a file
def save_private_key(private_key, folder_path):
    # Define the path for the private key file
    private_key_path = os.path.join(folder_path, "private_key.pem")

    # Write the private key to the file in PEM format
    with open(private_key_path, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),  # No passphrase (unencrypted)
            )
        )
    print(f"Private key saved as '{private_key_path}'")


# Function to save the public key to a file
def save_public_key(private_key, folder_path):
    # Extract the public key from the private key
    public_key = private_key.public_key()

    # Define the path for the public key file
    public_key_path = os.path.join(folder_path, "public_key.pem")

    # Write the public key to the file in PEM format
    with open(public_key_path, "wb") as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )
    print(f"Public key saved as '{public_key_path}'")


# Main function
def main(save_path):
    # Create the 'save_path' folder if it doesn't exist
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # Generate the RSA key pair (private and public keys)
    private_key = generate_rsa_keypair()

    # Save both the private and public keys to disk
    save_private_key(private_key, save_path)
    save_public_key(private_key, save_path)

# Entry point of the script
if __name__ == "__main__":
    # Create ArgumentParser object
    parser = argparse.ArgumentParser(description="Save RSA key pair to the specified directory.")

    # Add argument for the folder path
    parser.add_argument(
        "-p", "--path", 
        type=str, 
        default="keys",  # Default path if no argument is provided
        help="The folder path where you want to save the keys. Default is 'keys'."
    )

    # Parse the arguments
    args = parser.parse_args()

    # Call the main function with the provided folder path
    main(args.path)
