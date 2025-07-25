#!/usr/bin/env python3
import sys
import os
import subprocess

def run_wlst_script(wlst_script):
    """Execute WLST script with proper output handling"""
    try:
        # Using check_call for better error handling
        subprocess.check_call(
            ['wlst.sh', wlst_script],
            stdout=sys.stdout,  # Direct output to console
            stderr=subprocess.STDOUT,
            bufsize=1,  # Line buffering
            universal_newlines=True
        )
    except subprocess.CalledProcessError as e:
        print(f"::error::WLST execution failed with code {e.returncode}", flush=True)
        sys.exit(e.returncode)

def main():
    # Immediate debug marker
    print("::debug::Starting MFT deployment script", flush=True)
    
    if len(sys.argv) != 9:
        print("::error::Incorrect arguments", flush=True)
        print("Usage: python deploy_mft.py <user> <pass> <url> <project> <version> <artifacts> <export> <config>", flush=True)
        sys.exit(1)
    
    args = {
        'username': sys.argv[1],
        'password': "********",  # Masked for security
        'url': sys.argv[3],
        'project': sys.argv[4],
        'version': sys.argv[5],
        'artifacts_file': sys.argv[6],
        'export_zip': sys.argv[7],
        'config_xml': sys.argv[8]
    }

    # Print arguments in GitHub-friendly format
    print("::group::📋 Deployment Arguments", flush=True)
    print(f"Username      : {args['username']}", flush=True)
    print(f"Password      : {args['password']}", flush=True)
    print(f"URL           : {args['url']}", flush=True)
    print(f"Project       : {args['project']}", flush=True)
    print(f"Version       : {args['version']}", flush=True)
    print(f"Artifacts File: {args['artifacts_file']}", flush=True)
    print(f"Export ZIP    : {args['export_zip']}", flush=True)
    print(f"Config XML    : {args['config_xml']}", flush=True)
    print("::endgroup::", flush=True)

    # Validate files exist
    for f in [args['artifacts_file'], args['export_zip']]:
        if not os.path.exists(f):
            print(f"::error::File not found - {f}", flush=True)
            sys.exit(1)
    
    print(f"::notice::🚀 Starting MFT Deployment for {args['project']} v{args['version']}", flush=True)
    
    # Generate temporary WLST script
    try:
        with open('temp_deploy.py', 'w') as f:
            f.write(f"""
from java.lang import System
from oracle.mft.wlst import importMftMetadata, bulkDeployArtifact

print("\\n::group::🌐 MFT Server Connection")
print("Connecting to: {args['url']}")
connect('{sys.argv[1]}', '{sys.argv[2]}', '{args['url']}')
print("::endgroup::")

print("::group::📦 Importing Configuration")
print("Source: {args['export_zip']}")
importMftMetadata('{args['export_zip']}', '{args['config_xml'] if args['config_xml'] != 'none' else ''}')
print("::endgroup::")

print("::group::🛠️ Artifact Deployment")
with open('{args['artifacts_file']}') as artifacts:
    for line in artifacts:
        line = line.strip()
        if line and not line.startswith("#"):
            parts = line.split(':', 1)
            artifact_type = parts[0].strip().upper() if len(parts) > 1 else 'TRANSFER'
            artifact_name = parts[1].strip() if len(parts) > 1 else line
            print(f"Deploying {{artifact_type}}:{{artifact_name}}")
            bulkDeployArtifact(artifact_type, artifact_name, '{args['project']} deployment')
            print(f"✓ Success: {{artifact_type}}:{{artifact_name}}")
print("::endgroup::")

print("::notice title=Deployment Complete::✅ All artifacts deployed successfully")
disconnect()
""")
        
        print("::debug::WLST script generated successfully", flush=True)
        run_wlst_script('temp_deploy.py')
        
    except Exception as e:
        print(f"::error::Script generation failed: {str(e)}", flush=True)
        sys.exit(1)

if __name__ == "__main__":
    main()