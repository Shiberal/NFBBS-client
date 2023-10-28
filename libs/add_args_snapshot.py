import requests
import os
def add_args_snapshot(args, base_url, headers, folder_path):
    if args.snapshot:
        if args.deletesnapshot:
        # Construct the URL for deleting the snapshot
            delete_snapshot_url = f"{base_url}/{args.bucket}/{args.snapshot}/deletesnapshot"

        # Send a DELETE request to delete the snapshot
            delete_snapshot_response = requests.get(
            delete_snapshot_url, headers=headers)
            if delete_snapshot_response.status_code == 200:
                print(f"Deleted snapshot: {args.snapshot}")
            else:
                print(
                f"Failed to delete snapshot: {args.snapshot}. Status code: {delete_snapshot_response.status_code}")
                exit(1)
        elif args.list:
        # Construct the URL for listing the contents of the snapshot
            list_snapshot_url = f"{base_url}/{args.bucket}/{args.snapshot}/list"

        # Send a GET request to list the contents of the snapshot
            list_snapshot_response = requests.get(
            list_snapshot_url, headers=headers)
            if list_snapshot_response.status_code == 200:
                snapshot_contents = list_snapshot_response.json()
                print(f"Contents of snapshot: {args.snapshot}")
                for item in snapshot_contents:
                    print(item)
            else:
                print(
                f"Failed to list contents of snapshot: {args.snapshot}. Status code: {list_snapshot_response.status_code}")
                exit(1)
        elif args.restore:
            list_all_url = f"{base_url}/{args.bucket}/{args.snapshot}/listall"
            list_all_response = requests.get(list_all_url, headers=headers)
            print(list_all_response.text)

            if list_all_response.status_code == 200:
                for item in list_all_response.json():
                    get_file_url = f"{base_url}/{args.bucket}/{args.snapshot}/getfile"
                    get_file_url = f"{get_file_url}/?name={item}"
                    
                    # Send a GET request to download a file from the snapshot
                    download_response = requests.get(get_file_url, headers=headers)
                    
                    if download_response.status_code == 200:
                        # Determine the file path to save the restored file within folder_path
                        file_path = os.path.join(folder_path, item)
                        
                        # Ensure the directory structure exists
                        directory_path = os.path.dirname(file_path)
                        os.makedirs(directory_path, exist_ok=True)
                        
                        # Save the downloaded file to the specified destination
                        with open(file_path, 'wb') as file:
                            file.write(download_response.content)
                        print(f"Restored file: {item} to {file_path}")
                    else:
                        print(f"Failed to download file: {item}. Status code: {download_response.status_code}")
            else:
                print(f"Failed to list all items in snapshot: {args.snapshot}. Status code: {list_all_response.status_code}")
                exit(1)
            
        elif args.get:
            if not args.dest:
                print("You must provide a destination path using --dest when using --get.")
                exit(1)

            # Construct the URL for downloading a file from the snapshot
            get_file_url = f"{base_url}/{args.bucket}/{args.snapshot}/getfile"
            get_file_url = f"{get_file_url}/?name={args.get}"

            # Send a GET request to download a file from the snapshot
            download_response = requests.get(get_file_url, headers=headers)
            if download_response.status_code == 200:
                # Save the downloaded file to the specified destination
                with open(args.dest+"/"+args.get, 'wb') as file:
                    file.write(download_response.content)
                print(f"Downloaded file '{args.get}' from snapshot: {args.snapshot} to '{args.dest}'")
            else:
                print(
                    f"Failed to download file '{args.get}' from snapshot: {args.snapshot}. Status code: {download_response.status_code}")
                exit(1)