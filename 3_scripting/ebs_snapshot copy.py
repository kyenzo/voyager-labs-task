import boto3
import argparse

# Initialize boto3 client for EC2
ec2 = boto3.client('ec2')

def create_snapshot(volume_id, snapshot_name):
    """Creates a snapshot with the given name for the specified EBS volume."""
    description = f"Snapshot of volume {volume_id} - {snapshot_name}"
    snapshot = ec2.create_snapshot(
        VolumeId=volume_id,
        Description=description,
        TagSpecifications=[
            {
                'ResourceType': 'snapshot',
                'Tags': [
                    {'Key': 'Name', 'Value': snapshot_name}
                ]
            }
        ]
    )
    print(f"Created snapshot: {snapshot['SnapshotId']}")
    return snapshot['SnapshotId']

def delete_old_snapshots(volume_id, retain_count):
    """Deletes old snapshots for the specified volume, keeping only the latest ones."""
    snapshots = ec2.describe_snapshots(
        Filters=[
            {'Name': 'volume-id', 'Values': [volume_id]},
        ],
        OwnerIds=['self']  # Only snapshots owned by this account
    )['Snapshots']
    
    # Sort snapshots by creation date, newest first
    snapshots.sort(key=lambda x: x['StartTime'], reverse=True)
    
    # Identify snapshots to delete
    snapshots_to_delete = snapshots[retain_count:]
    for snapshot in snapshots_to_delete:
        ec2.delete_snapshot(SnapshotId=snapshot['SnapshotId'])
        print(f"Deleted old snapshot: {snapshot['SnapshotId']}")

def main():
    parser = argparse.ArgumentParser(description="Take EBS snapshots and manage retention")
    parser.add_argument("snapshot_name", help="Name for the snapshot")
    parser.add_argument("volume_id", help="EBS volume ID")
    parser.add_argument("retain_count", type=int, help="Number of recent snapshots to retain")
    
    args = parser.parse_args()
    
    # Create a new snapshot
    create_snapshot(args.volume_id, args.snapshot_name)
    
    # Delete older snapshots
    delete_old_snapshots(args.volume_id, args.retain_count)

if __name__ == "__main__":
    main()
