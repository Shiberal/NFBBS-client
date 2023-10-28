import requests
import os
def add_args_backup(args, base_url, folder_path, bucket_name, headers):
    if args.backup:
    # Step 1: Get a new snapshot
        snapshot_response = requests.get(
    f"{base_url}/{args.bucket}/newsnapshot", headers=headers)
        if snapshot_response.status_code != 200:
            print(
            f"Failed to create a new snapshot. Status code: {snapshot_response.status_code}")
            exit(1)

        snapshot_name = snapshot_response.text
        print(f"Created a new snapshot: {snapshot_name}")


        folder_path = os.path.abspath(folder_path)  # Get the absolute path
        print(f"Backup folder: {folder_path}")
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, folder_path)

            # Construct the URL for adding a file to the snapshot
                add_file_url = f"{base_url}/{args.bucket}/{snapshot_name}/addFile"
                data = {'name': relative_path}

            # Upload the file
                with open(file_path, 'rb') as file_data:
                    files = {'file': (relative_path, file_data)}
                    print(file_path)
                    print(relative_path)
                    upload_response = requests.post(
                    f'{base_url}/{bucket_name}/{snapshot_name}/addFile?name={relative_path}', headers=headers, data=data, files={'file': file_data})
                    if upload_response.status_code == 200:
                        print(f"Uploaded file: {relative_path}")
                    else:
                        print(
                        f"Failed to upload file: {relative_path}. Status code: {upload_response.status_code}")