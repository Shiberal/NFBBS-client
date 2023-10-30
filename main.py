import json
import argparse
import requests
from libs.add_args_snapshot import add_args_snapshot
from libs.add_args_backup import add_args_backup


# Create an argument parser
parser = argparse.ArgumentParser(
    description='Interact with an HTTP backend protected with a token.')


parser.add_argument("--newbucket", help="Create a new bucket")
parser.add_argument('--bucket', required=False,
                    help='Specify the bucket name from the JSON configuration.')
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
parser.add_argument("--auth",help="Authenticate to the server")
parser.add_argument("--url",help="url")
parser.add_argument('--backup', action='store_true',
                    help='Enable backup option.')





args = parser.parse_args()
folder_path = ""
bucket_name = ""
token = ""

# Load the JSON configuration from a file
with open('config.json', 'r') as config_file:
    config_data = json.load(config_file)


if args.bucket:
    # Find the specified bucket in the configuration
    bucket_to_use = None
    for bucket in config_data['buckets']:
        if bucket['bucket'] == args.bucket:
            folder_path = bucket['folder']
            bucket_name = bucket['bucket']
            incremental = bucket['incremental']
            bucket_auth = bucket['authname']
            break

    for auth_data in config_data['auth']:
        if auth_data['authname'] == bucket_auth:
            
            token = auth_data['token'];
            base_url = auth_data['url'];
    
    if not bucket_name:
        print(f"Bucket '{args.bucket}' not found in the JSON configuration.")
        exit(1)



if args.auth:
    for auth_data in config_data['auth']:
        if auth_data['authname'] == args.auth:
            token = auth_data['token'];
            base_url = auth_data['url'];


if args.url: base_url = args.url;



# Check if the token is provided
if not token:
    print("Token missing in the configuration.")
    exit(1)

# Construct the headers with the token
headers = {'Authorization': f'Basic {token}'}


if args.list:
            
            print (token)
            print (base_url)

        # Construct the URL for listing the contents of the bucket
            list_bucket_url = f"{base_url}/list"
            if len(bucket_name) > 0:
                list_bucket_url = f"{base_url}/{bucket_name}/list"

        # Send a GET request to list the contents of the snapshot
            list_bucket_response = requests.get(
            list_bucket_url, headers=headers)
            if list_bucket_response.status_code == 200:
                snapshot_contents = list_bucket_response.json()
                print(f"Contents of snapshot: {args.snapshot}")
                for item in snapshot_contents:
                    print(item)
            else:
                print(
                f"Failed to list contents of snapshot: {args.snapshot}. Status code: {list_bucket_response.status_code}")
                exit(1)

if args.newbucket:
    #new bucket /newbucket takes the name of the new bucket as query name
    new_bucket_url = f"{base_url}/newbucket?name={args.newbucket}"
    print(new_bucket_url);
    new_bucket_response = requests.get(new_bucket_url, headers=headers)
    if new_bucket_response.status_code == 200:
            print(f"{new_bucket_response.text}")
            exit(0)

if args.deletebucket:
    #new bucket /newbucket takes the name of the new bucket as query name
    if len(bucket_name) > 0:
        new_bucket_url = f"{base_url}/{bucket_name}/deletebucket"
        print(new_bucket_url);
        new_bucket_response = requests.get(new_bucket_url, headers=headers)
        if new_bucket_response.status_code == 200:
                print(f"{new_bucket_response.text}")
                exit(0)
    print("--bucket bucketname")


if len(folder_path) > 0:
    add_args_backup(args, base_url, folder_path, bucket_name, headers, incremental)
    add_args_snapshot(args, base_url, headers,folder_path)