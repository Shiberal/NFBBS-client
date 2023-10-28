import json
import argparse

from libs.add_args_snapshot import add_args_snapshot
from libs.add_args_backup import add_args_backup



# Create an argument parser
parser = argparse.ArgumentParser(
    description='Interact with an HTTP backend protected with a token.')

# Add command-line arguments
parser.add_argument('--bucket', required=True,
                    help='Specify the bucket name from the JSON configuration.')

# Optional actions
parser.add_argument('--deletebucket', action='store_true',
                    help='Delete the specified bucket.')
parser.add_argument(
    '--snapshot', help='Specify the snapshot name for further actions.')
parser.add_argument('--deletesnapshot', action='store_true',
                    help='Delete the specified snapshot.')
parser.add_argument('--list', action='store_true',
                    help='List the contents of a snapshot.')
parser.add_argument('--get', help='Download a file from the snapshot.')
parser.add_argument("--dest", help="Destination path for the downloaded file")
parser.add_argument("--restore",action='store_true', help="Restore a folder to the given snapshot")

# Add a global flag for backup
parser.add_argument('--backup', action='store_true',
                    help='Enable backup option.')

# Parse the command-line arguments
args = parser.parse_args()

# Load the JSON configuration from a file
with open('config.json', 'r') as config_file:
    config_data = json.load(config_file)


# Find the specified bucket in the configuration
bucket_to_use = None
for bucket in config_data['buckets']:
    if bucket['bucket'] == args.bucket:
        bucket_to_use = bucket
        break

if not bucket_to_use:
    print(f"Bucket '{args.bucket}' not found in the JSON configuration.")
    exit(1)

base_url = bucket_to_use['base_url']
folder_path = bucket_to_use['folder']
bucket_name = bucket_to_use['bucket']
token = bucket_to_use.get('token', '')  # Get the token from the configuration

# Check if the token is provided
if not token:
    print("Token missing in the configuration.")
    exit(1)

# Construct the headers with the token
headers = {'Authorization': f'Basic {token}'}

add_args_backup(args, base_url, folder_path, bucket_name, headers)
add_args_snapshot(args, base_url, headers,folder_path)
