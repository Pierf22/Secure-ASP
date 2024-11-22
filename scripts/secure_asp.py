import argparse
import os
import requests
import urllib3
import re

# Disable the SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def check_extension(filename, extensions):
    """
    Checks if the file has one of the specified extensions.
    """
    if not any(filename.endswith(ext) for ext in extensions):
        raise argparse.ArgumentTypeError(
            f"The file {filename} must have one of the following extensions: {', '.join(extensions)}."
        )
    if not os.path.isfile(filename):
        raise argparse.ArgumentTypeError(f"The file {filename} does not exist.")
    return filename


def send_files(asp_file, pem_file, output_dir):
    """
    Sends the files to the local server (localhost:8000/v1/encodings/verify).
    """
    url = "https://localhost:8000/v1/encodings/verify"

    # Open the files in binary mode
    with open(asp_file, "rb") as asp, open(pem_file, "rb") as pem:
        files = {"encoding_file": asp, "certificate_file": pem}

        # Send a POST request with the files
        try:
            response = requests.post(url, files=files, verify=False)
        except Exception as e:
            print(f"Failed to upload files. Exception: {e}")
            return
        # Check the response from the server
        if response.status_code == 200:
            print("Files uploaded successfully.")
        
            # Extract filename from the header
            content_disposition = response.headers.get("Content-Disposition", "")
            file_name = "downloaded_file"  # Default filename if none is provided
        
            # Parse filename from Content-Disposition header
            if "filename=" in content_disposition:
                file_name = content_disposition.split("filename=")[-1].strip('"')
            
            file_name = os.path.join(output_dir, file_name)
            # Save the content to a file
            with open(file_name, "wb") as f:
                f.write(response.content)
        
            print(f"File downloaded successfully as {file_name}.")
            file_str = response.content.decode("utf-8")
            # Extract 'File name', 'Signed by', and 'Last update' using regular expressions
            file_name_match = re.search(r"%Encoding name : (.+)", file_str)
            signed_by_match = re.search(r"%Signed by : (.+)", file_str)
            last_update_match = re.search(r"%Last update : (.+)", file_str)

            # Print the extracted information
            if file_name_match:
                print("Encoding name:", file_name_match.group(1))
            else:
                print("Encoding name: -")

            if signed_by_match:
                print("Signed by:", signed_by_match.group(1))
            else:
                print("Signed by: -")

            if last_update_match:
                print("Last update:", last_update_match.group(1))
            else:
                print("Last update: -")
        else:
            print(f"Failed to upload files. Status code: {response.status_code}")
            print("Response:", response.text)


def main():
    # Create an argument parser
    parser = argparse.ArgumentParser(
        description="Process an .asp or .txt file and an intermediate .pem certificate file, then send them to the server."
    )

    # Argument for the .asp or .txt file, with validation
    parser.add_argument(
        "asp_file",
        type=lambda f: check_extension(f, [".asp", ".txt"]),
        help="The .asp or .txt file to be processed",
    )

    # Argument for the .pem file, with validation
    parser.add_argument(
        "pem_file",
        type=lambda f: check_extension(f, [".pem"]),
        help="The intermediate .pem certificate file",
    )

    # Optional argument for the directory to save the decrypted file
    parser.add_argument(
        "--output_dir",
        type=str,
        default=".",
        help="The directory path to save the decrypted file (optional)",
    )

    # Parse the arguments
    args = parser.parse_args()

    # Ensure the specified output directory exists
    if not os.path.isdir(args.output_dir):
        print(f"The specified output directory '{args.output_dir}' does not exist.")
        return

    # Print the files being processed
    print(f"Processing ASP/TXT file: {args.asp_file}")
    print(f"Processing PEM certificate file: {args.pem_file}")
    print(f"Output directory: {args.output_dir}")

    # Send the files to the server and save the decrypted file in the specified directory
    send_files(args.asp_file, args.pem_file, args.output_dir)



if __name__ == "__main__":
    main()
