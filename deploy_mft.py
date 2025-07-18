# Python Script (mft/deploy_mft.py)
import sys
import os
from java.lang import System

def validate_inputs(args):
    required_files = {
        'artifacts': args['artifacts_file'],
        'export': args['export_zip'],
        'config': args['config_xml']
    }
    for name, path in required_files.items():
        if not os.path.exists(path):
            print(f"❌ Missing {name} file: {path}")
            sys.exit(1)

def process_artifacts(file_path, project):
    deployed = {'SOURCE': 0, 'TARGET': 0, 'TRANSFER': 0}
    
    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split(':', 1)
            if len(parts) == 2:
                artifact_type, artifact_name = parts[0].strip().upper(), parts[1].strip()
                if artifact_type not in ('SOURCE', 'TARGET', 'TRANSFER'):
                    print(f"⚠️ Unknown artifact type '{artifact_type}', defaulting to TRANSFER")
                    artifact_type = 'TRANSFER'
            else:
                artifact_type, artifact_name = 'TRANSFER', line

            try:
                # MFT Deployment
                print(f"\n🌐 Connecting to MFT server {args['url']}")
                connect(args['username'], args['password'], args['url'])  

                # Import Config
                print(f"\n📦 Importing configuration from {args['export_zip']}")
                importMftMetadata(args['export_zip'], args['config_xml'])

                bulkDeployArtifact(artifact_type, artifact_name, f'{project} deployment')
                deployed[artifact_type] += 1
                print(f"✓ Deployed {artifact_type}:{artifact_name}")
            except:
                print(f"✗ Failed to deploy {artifact_type}:{artifact_name}")
                dumpStack()

    print("\n📊 Deployment Summary:")
    for k, v in deployed.items():
        print(f"{k}: {v}")

def main():
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

    try:
        print(f"\n🚀 Starting MFT Deployment for {args['project']} v{args['version']}")
        validate_inputs(args)
        process_artifacts(args['artifacts_file'], args['project'])
        print(f"\n✅ Successfully deployed {args['project']} v{args['version']}")
        disconnect()
    except:
        print(f"\n❌ Critical failure deploying {args['project']}")
        dumpStack()
        sys.exit(1)

if __name__ == "__main__":
    main()
