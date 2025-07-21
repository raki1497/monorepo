# Modified deploy_mft.py (works with standard Python)
import sys
import os
import subprocess

def run_wlst_script(wlst_script, *args):
    wlst_cmd = [
        f"\home\raki\Oracle\Middleware\Oracle_Home\wlserver\common\bin\wlst.sh",
        wlst_script
    ] + list(args)
    
    result = subprocess.run(wlst_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"WLST Error: {result.stderr}")
        sys.exit(1)
    return result.stdout

def main():
    if len(sys.argv) != 9:
        print("Usage: python deploy_mft.py <user> <pass> <url> <project> <version> <artifacts> <export> <config>")
        sys.exit(1)
    
    args = {
        'username': sys.argv[1],
        'password': sys.argv[2],
        'url': sys.argv[3],
        'project': sys.argv[4],
        'version': sys.argv[5],
        'artifacts_file': sys.argv[6],
        'export_zip': sys.argv[7],
        'config_xml': sys.argv[8]
    }
    
    # Validate files exist
    for f in [args['artifacts_file'], args['export_zip']]:
        if not os.path.exists(f):
            print(f"Error: File not found - {f}")
            sys.exit(1)
    
    print(f"\n🚀 Starting MFT Deployment for {args['project']} v{args['version']}")
    
    # Generate temporary WLST script
    with open('temp_deploy.py', 'w') as f:
        f.write(f"""
from java.lang import System
from oracle.mft.wlst import importMftMetadata, bulkDeployArtifact

print("\\n🌐 Connecting to MFT server {args['url']}")
connect('{args['username']}', '{args['password']}', '{args['url']}')

print("\\n📦 Importing configuration from {args['export_zip']}")
importMftMetadata('{args['export_zip']}', '{args['config_xml'] if args['config_xml'] != 'none' else ''}')

with open('{args['artifacts_file']}') as artifacts:
    for line in artifacts:
        line = line.strip()
        if line and not line.startswith("#"):
            parts = line.split(':', 1)
            artifact_type = parts[0].strip().upper() if len(parts) > 1 else 'TRANSFER'
            artifact_name = parts[1].strip() if len(parts) > 1 else line
            bulkDeployArtifact(artifact_type, artifact_name, '{args['project']} deployment')
            print(f"✓ Deployed {{artifact_type}}:{{artifact_name}}")

disconnect()
print("\\n✅ Deployment completed successfully")
""")
    
    # Execute the WLST script
    run_wlst_script('temp_deploy.py')
    
if __name__ == "__main__":
    main()
