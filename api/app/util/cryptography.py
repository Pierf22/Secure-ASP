from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID
from cryptography import x509
import os
import base64
import re
from datetime import timezone, datetime, timedelta
import logging
import uuid
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

logger = logging.getLogger(__name__)


def check_signature(file_content: bytes, signature: str, public_key_pem: str) -> bool:
    # Remove -----BEGIN SIGNATURE----- and -----END SIGNATURE----- if present
    signature = re.sub(
        r"-----BEGIN SIGNATURE-----|-----END SIGNATURE-----", "", signature
    ).strip()
    logger.debug(signature)
    logger.debug(public_key_pem)
    # Decode the Base64 signature
    try:
        decoded_signature = base64.b64decode(signature)
    except Exception as e:
        logger.debug(f"Failed to decode signature: {e}")
        return False
    logger.debug(f"Decoded signature: {decoded_signature}")
    logger.debug(f"File content: {file_content}")

    # Load the public key from PEM format (RSA in this case)
    try:
        public_key = serialization.load_pem_public_key(public_key_pem.encode())
    except Exception as e:
        logger.debug(f"Failed to load public key: {e}")
        return False

    # Verify the signature using the public key, the file content, and SHA-256
    try:
        public_key.verify(
            decoded_signature,
            file_content,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )
        return True
    except Exception as e:
        logger.debug(f"Signature verification failed: {e}")
        return False


def encrypt(file: bytes) -> bytes:
    root_cert = load_root_certificate_from_file()
    # Generate a random AES key and IV
    aes_key = os.urandom(32)  # AES key of 32 bytes
    iv = os.urandom(16)  # Initialization vector of 16 bytes
    cipher_aes = Cipher(
        algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend()
    )
    encryptor = cipher_aes.encryptor()

    ciphertext = encryptor.update(file) + encryptor.finalize()
    logger.debug(f"My public key: {root_cert.public_key()}")
    encrypted_aes_key = root_cert.public_key().encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    return iv + encrypted_aes_key + ciphertext


def decrypt(encrypted_data: bytes) -> bytes:
    private_key = load_private_key_from_file()
    # Extract the IV (first 16 bytes), the encrypted AES key, and the ciphertext
    iv = encrypted_data[:16]  # IV is 16 bytes long
    encrypted_aes_key = encrypted_data[
        16 : 16 + private_key.key_size // 8
    ]  # AES key size is based on the RSA key size
    ciphertext = encrypted_data[
        16 + private_key.key_size // 8 :
    ]  # The rest is the encrypted file

    # Decrypt the AES key using the RSA private key
    aes_key = private_key.decrypt(
        encrypted_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    # Use the decrypted AES key and IV to create the AES cipher for decryption
    cipher_aes = Cipher(
        algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend()
    )
    decryptor = cipher_aes.decryptor()

    # Decrypt the file (ciphertext) using AES
    decrypted_file = decryptor.update(ciphertext) + decryptor.finalize()

    # Return the decrypted file content
    return decrypted_file


def generate_certificate(
    user_id: uuid.UUID, csr_request_pem: str
):  # generate a intermediate certificate

    root_cert = load_root_certificate_from_file()
    root_key = load_private_key_from_file()
    logger.debug(root_cert)
    # Load the CSR from the PEM file
    csr = x509.load_pem_x509_csr(csr_request_pem.encode("utf-8"))
    # Ensure the CSR is valid
    if not csr.is_signature_valid:
        raise ValueError("Invalid CSR signature")
    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "IT"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Calabria"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Rende"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Secure ASP"),
            x509.NameAttribute(NameOID.COMMON_NAME, str(user_id)),
        ]
    )
    int_cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(root_cert.subject)
        .public_key(csr.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(
            datetime.now(timezone.utc) + timedelta(days=1000)
        )
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=0),
            critical=True,
        )
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_subject_key_identifier(
                root_cert.extensions.get_extension_for_class(
                    x509.SubjectKeyIdentifier
                ).value
            ),
            critical=False,
        )
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(csr.public_key()), critical=False
        )
        .sign(root_key, hashes.SHA256())
    )

    public_key = (
        csr.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode("utf-8")
    )
    # Serialize the intermediate certificate to PEM format
    cert_pem = int_cert.public_bytes(encoding=serialization.Encoding.PEM).decode(
        "utf-8"
    )

    # Return the cert and the user public key
    return cert_pem, public_key


def load_root_certificate_from_file():
    base_path = os.path.dirname(__file__)

    cert_path = os.path.abspath(
        os.path.join(base_path, "..", "..", "resources", "ssl_cert", "cert.pem")
    )
    with open(cert_path, "rb") as cert_file:
        cert_data = cert_file.read()

    try:
        certificate = x509.load_pem_x509_certificate(cert_data, default_backend())
    except ValueError:
        raise ValueError("Invalid certificate file")
    return certificate


def load_private_key_from_file():
    base_path = os.path.dirname(__file__)

    key_path = os.path.abspath(
        os.path.join(base_path, "..", "..", "resources", "ssl_cert", "key.pem")
    )
    with open(key_path, "rb") as key_file:
        key_data = key_file.read()

    private_key = serialization.load_pem_private_key(
        key_data, password=None, backend=default_backend()
    )

    return private_key


def generate_encoding_file(encoding: bytes, signature: bytes, owner:str, file_name:str) -> bytes:
    # Decode the signature content 
    signature_str = signature.decode("utf-8")

    # Add BEGIN and END delimiters if missing
    if not re.search(r"-----BEGIN SIGNATURE-----", signature_str):
        signature_str = "-----BEGIN SIGNATURE-----\n" + signature_str

    if not re.search(r"-----END SIGNATURE-----", signature_str):
        signature_str += "\n-----END SIGNATURE-----"

  # Format the date to show only month, day, and year
    formatted_date = datetime.now(timezone.utc).strftime("%d %B %Y %H:%M:%S UTC")



    # Add the owner, file name, and formatted date to the signature
    info_lines = (
        f"Secure ASP - Signed file\n"
        f"Encoding name : {file_name}\n"
        f"Signed by : {owner}\n"
        f"Last update : {formatted_date}\n"
    )
    signature_str = info_lines + signature_str

    # add % at start of every signature line
    signature_str = '\n'.join('%' + line for line in signature_str.splitlines())

     # add \n if missing
    if not signature_str.endswith("\n"):
        signature_str += "\n"

    #    Combine the signature and file content
    combined_content = signature_str.encode("utf-8") + encoding

    logger.debug(f"Combined content: {combined_content}")

    # encrypt the combined content
    return encrypt(combined_content)


def verify_certificate(certificate: bytes) -> uuid.UUID:
    # Load the root certificate (your private CA certificate)
    root_cert = load_root_certificate_from_file()

    try:
        # Load the provided certificate from bytes
        cert = x509.load_pem_x509_certificate(certificate, default_backend())
    except ValueError:
        logger.debug("Invalid certificate file")
        return None

    try:
        # Verify the provided certificate was signed by the root certificate
        root_cert.public_key().verify(
            cert.signature,
            cert.tbs_certificate_bytes,  # The content that was signed
            padding.PKCS1v15(),
            cert.signature_hash_algorithm,
        )
    except Exception as e:
        logger.debug(f"Certificate verification failed: {e}")
        raise None
    
    # Check the expiration date
    current_time = datetime.now(timezone.utc)
    if current_time < cert.not_valid_before_utc or current_time > cert.not_valid_after_utc:
        logger.debug("Certificate is expired or not yet valid")
        return None

    # Extract the Common Name (CN) which is assumed to be a UUID
    common_name = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    try:
        # Convert the CN (Common Name) to a UUID
        return uuid.UUID(common_name)
    except ValueError:
        logger.debug("Invalid UUID in certificate")
        raise None


def split_encoding_and_signature(decrypted_file_content: bytes) -> tuple[bytes, bytes]:
    """
    Splits the decrypted file content into the signature and the actual file content.
    The file contains both the signature and the encoded content.

    :param decrypted_file_content: The decrypted file content (bytes) which contains both the signature and the actual content.
    :return: A tuple (signature: bytes, content: bytes) containing the signature and the file content.
    """

    # Decode the file content to work with it as a string
    try:
        file_str = decrypted_file_content.decode("utf-8")
    except UnicodeDecodeError:
        raise ValueError("Failed to decode the decrypted file content.")

    # Find the signature part in the file
    signature_match = re.search(
        r"%-----BEGIN SIGNATURE-----(.*?)%-----END SIGNATURE-----", file_str, re.DOTALL
    )

    if not signature_match:
        raise ValueError("No valid signature found in the file.")
    logger.debug(f"all file: {file_str}")

    # Extract the signature (between BEGIN and END SIGNATURE)
    signature_str = signature_match.group(1).strip()
    
    # Remove % at the start of each line in the extracted signature
    signature_str = '\n'.join(line[1:] if line.startswith('%') else line for line in signature_str.splitlines())

    # Extract the actual file content (the part of the file that is not the signature)
    content_without_signature = re.sub(
        r"%-----BEGIN SIGNATURE-----(.*?)%-----END SIGNATURE-----\s*",
        "",
        file_str,
        flags=re.DOTALL,
    )
    # remove the info lines
    content_without_signature = re.sub(
        r"%?Secure ASP - Signed file\n"
        r"%?Encoding name : .*\n"
        r"%?Signed by : .*\n"
        r"%?Last update : .*\n",
        "",
        content_without_signature,
        flags=re.MULTILINE,
    ).encode("utf-8")
    logger.debug(f"Signature: {signature_str}")
    logger.debug(f"Content: {content_without_signature}")

    # Return the signature and the content as bytes
    return signature_str, content_without_signature
