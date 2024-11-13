import subprocess 
import time
import re 
from datetime import datetime, timedelta
  
# Define the Git commands
commands = {
    'status': 'git status --porcelain',
    'add': 'git add "{filename}"',  # Adding quotes to handle spaces
    'commit': 'git commit -m "Created for {filename}"',
    'push': 'git push origin main'
}

def run_command(command, filename=None):
    if filename:
        command = command.format(filename=filename)
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result

def parse_git_status(status_output):
    # Use regex to match file paths, including directories and files with spaces
    pattern = r'^[ MADRCU?]{1,2} (.+)$'
    return re.findall(pattern, status_output, re.MULTILINE)

def main():
    while True:
        # Get the current time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Check the status of the Git repository
        result = run_command(commands['status'])
        status_output = result.stdout.strip()
        
        if status_output:
            # Parse the status output to get the list of files or folders
            items = parse_git_status(status_output)
            tot_items = len(items)
            if items:
                # Show all untracked or modified files
                print(f'[{current_time}] Detected {tot_items} untracked/modified files:')
                for item in items:
                    print(f'- {item}')
                
                # Proceed to process files one by one
                for filename in items:
                    print(f'[{current_time}] Processing file: {filename}')
                    
                    # Add the file
                    add_result = run_command(commands['add'], filename)
                    if add_result.returncode != 0:
                        print(f'Failed to add the file: {filename}')
                        print(add_result.stderr)
                        continue  # Skip this file and move to the next one
                    
                    # Commit the changes
                    commit_result = run_command(commands['commit'], filename)
                    if commit_result.returncode != 0:
                        print(f'Failed to commit the file: {filename}')
                        print(commit_result.stderr)
                        continue  # Skip this file and move to the next one
                    
                    # Push the changes
                    push_result = run_command(commands['push'])
                    if push_result.returncode == 0:
                        print(f'Successfully pushed the file: {filename} at {current_time}')
                    else:
                        print(f'Failed to push the file: {filename}')
                        print(push_result.stderr)
                    
                    # Set the waiting time before processing the next file (e.g., 15 minutes)
                    waiting_time = 1200  # 30 minutes in seconds
                    next_check_time = (datetime.now() + timedelta(seconds=waiting_time)).strftime("%Y-%m-%d %H:%M:%S")
                    print(f'Next Git status will be checked after {int(waiting_time / 60)} minutes at {next_check_time}')
                    print('*************')          
                    # Sleep for the specified time
                    time.sleep(waiting_time)
        else:
            # If no files are untracked or modified, rest for a set amount of time
            rest_time = 1200  # 15 minutes in seconds
            print(f'[{current_time}] No Untracked or Modified Files Found. Resting for {int(rest_time / 60)} minutes.')
            
            next_check_time = (datetime.now() + timedelta(seconds=rest_time)).strftime("%Y-%m-%d %H:%M:%S")
            print(f'Next Git status will be checked at {next_check_time}')
            
            # Sleep for the rest time
            time.sleep(rest_time)
        
        print('*************') 
        print() 

if __name__ == "__main__":
    main()


