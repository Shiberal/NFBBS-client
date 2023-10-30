import hashlib
import requests
import os

def list_files_in_directory(root_dir):
    file_set = []
    for dir_, _, files in os.walk(root_dir):
        for file_name in files:
            rel_dir = os.path.relpath(dir_, root_dir)
            rel_file = os.path.join(rel_dir, file_name)
            file_set.append(rel_file)

    return file_set




def add_args_backup(args, base_url, folder_path, bucket_name, headers,_incremental):
    if args.backup:
        if _incremental == True:
            incremental = True  # Set to True if needed based on your settings
        else:
            incremental = False
        if incremental:
            print("Performing incremental backup")

        # Step 1: Get a list of all generated buckets (snapshots)
        list_response = requests.get(f"{base_url}/{bucket_name}/list", headers=headers)
        if list_response.status_code != 200:
            print(f"Failed to retrieve the list of snapshots (buckets). Status code: {list_response.status_code}")
            return

        snapshot_data = list_response.json()

        # Get the MD5 hashes of all snapshots
        all_snapshot_md5_hashes = {}

        for snapshot in snapshot_data:
            snapshot_name = snapshot['name']
            print(f'Checking snapshot: {snapshot_name}');

            # Get MD5 hashes from the current snapshot
            snapshot_md5_response = requests.get(f"{base_url}/{bucket_name}/{snapshot_name}/listallwhash", headers=headers)
            if snapshot_md5_response.status_code != 200:
                print(f"Failed to retrieve MD5 hashes from snapshot {snapshot_name}. Status code: {snapshot_md5_response.status_code}")
                continue

            snapshot_md5_data = snapshot_md5_response.json()
            snapshot_md5_hashes = {item['filename']: item['md5hash'] for item in snapshot_md5_data}

            all_snapshot_md5_hashes[snapshot_name] = snapshot_md5_hashes

        folder_path = os.path.abspath(folder_path)

        # Normalize the folder path for comparison
        normalized_folder_path = os.path.normpath(folder_path)

        # Create a new snapshot
        snapshot_response = requests.get(f"{base_url}/{bucket_name}/newsnapshot", headers=headers)
        if snapshot_response.status_code != 200:
            print(f"Failed to create a new snapshot. Status code: {snapshot_response.status_code}")
            return
        
        new_snapshot_name = snapshot_response.text
        print(f"Created a new snapshot: {new_snapshot_name}")
        last_snapshot_name = snapshot_data[-1]['name']
        print(f"Last snapshot: {last_snapshot_name}")

        # deleting files from the snapshot that no longer exist
        if(incremental):
            local_files = list_files_in_directory(folder_path)
            # from list_response get the last snapshot
            for filename in all_snapshot_md5_hashes[last_snapshot_name]:
                if filename not in local_files:
                    # File doesn't exist locally, proceed with deletion
                    if not os.path.exists(folder_path+"/"+filename):
                        # Send a request to delete the file from the snapshot
                        delete_response = requests.get(f"{base_url}/{bucket_name}/{new_snapshot_name}/deleteFile?path={filename}", headers=headers)
                        if delete_response.status_code == 200:
                            print(f"Deleted file {filename} from snapshot {new_snapshot_name}")
                        else:
                            print(f"Failed to delete file {filename} from snapshot {new_snapshot_name}. Status code: {delete_response.status_code}")
        else:
            #remove everything from current snapshot
            for filename in all_snapshot_md5_hashes[last_snapshot_name]:
                # Send a request to delete the file from the snapshot

                delete_response = requests.get(f"{base_url}/{bucket_name}/{new_snapshot_name}/deleteFile?path={filename}", headers=headers)
                if delete_response.status_code == 200:
                    print(f"Deleted file {filename} from snapshot {new_snapshot_name}")

        # Iterate through files in the folder
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, normalized_folder_path)

                # Check if the file is missing or different in any of the snapshots
                should_upload = True

                for snapshot_name, snapshot_md5_hashes in all_snapshot_md5_hashes.items():
                    if relative_path in snapshot_md5_hashes:
                        # Calculate the MD5 hash of the local file
                        with open(file_path, 'rb') as local_file:
                            local_md5 = hashlib.md5(local_file.read()).hexdigest()

                        if local_md5 == snapshot_md5_hashes[relative_path]:
                            should_upload = False
                            break  # No need to check further snapshots if the file is the same

                # The code block you provided is responsible for upload files to the snapshot if they need to be
                # added or updated.
                if should_upload or not incremental:
                    data = {'name': relative_path}
                    with open(file_path, 'rb') as file_data:
                        files = {'file': (relative_path, file_data)}
                        print(f"Uploading file: {f'{base_url}/{bucket_name}/{new_snapshot_name}/addFile?path={relative_path}'}")
                        upload_response = requests.post(
                            f'{base_url}/{bucket_name}/{new_snapshot_name}/addFile?name={relative_path}', headers=headers, data=data, files=files)
                        if upload_response.status_code == 200:
                            print(f"Uploaded file: {relative_path}")
                        else:
                            print(f"Failed to upload file: {relative_path}. Status code: {upload_response.status_code}")

       
