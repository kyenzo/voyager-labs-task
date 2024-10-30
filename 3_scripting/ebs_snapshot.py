import boto3
import argparse

def get_volumes(instance_id):
    """Retrieve all volume IDs attached to a specific instance."""
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances(InstanceIds=[instance_id])
    volumes = [device['Ebs']['VolumeId'] for device in response['Reservations'][0]['Instances'][0]['BlockDeviceMappings']]
    return volumes

def create_snapshot(volume_id, snapshot_name):
    """Create a snapshot for a specified volume."""
    ec2 = boto3.client('ec2')
    snapshot = ec2.create_snapshot(
        VolumeId=volume_id,
        Description=f"{snapshot_name} for volume {volume_id}",
        TagSpecifications=[
            {
                'ResourceType': 'snapshot',
                'Tags': [
                    {'Key': 'Name', 'Value': snapshot_name}
                ]
            }
        ]
    )
    print(f"Snapshot initiated: {snapshot['SnapshotId']} for volume {volume_id}")
    return snapshot['SnapshotId']

def manage_snapshots(instance_id, snapshot_name, retain_count):
    """Create snapshots for all volumes attached to an instance and delete older ones."""
    ec2 = boto3.client('ec2')
    volumes = get_volumes(instance_id)
    snapshot_ids = []

    for volume_id in volumes:
        snapshot_id = create_snapshot(volume_id, snapshot_name)
        snapshot_ids.append(snapshot_id)

        # Fetch and delete old snapshots for this volume
        snapshots = ec2.describe_snapshots(
            Filters=[{'Name': 'volume-id', 'Values': [volume_id]}],
            OwnerIds=['self']
        )['Snapshots']
        
        # Sort snapshots by StartTime to find oldest ones
        snapshots = sorted(snapshots, key=lambda x: x['StartTime'], reverse=True)
        old_snapshots = snapshots[retain_count:]  # Keep only the newest 'retain_count' snapshots

        for snapshot in old_snapshots:
            print(f"Deleting old snapshot: {snapshot['SnapshotId']} for volume {volume_id}")
            ec2.delete_snapshot(SnapshotId=snapshot['SnapshotId'])

    return snapshot_ids

def main():
    parser = argparse.ArgumentParser(description="Take EBS snapshots for all volumes attached to an EC2 instance.")
    parser.add_argument("snapshot_name", help="The name for the new snapshot.")
    parser.add_argument("instance_id", help="The EC2 instance ID.")
    parser.add_argument("retain_count", type=int, help="Number of snapshots to retain.")
    args = parser.parse_args()

    snapshot_ids = manage_snapshots(args.instance_id, args.snapshot_name, args.retain_count)
    print("Snapshot creation initiated for all volumes. Snapshot IDs:")
    for snapshot_id in snapshot_ids:
        print(snapshot_id)
    print("\nUse the following command to check snapshot statuses:")
    print("aws ec2 describe-snapshots --snapshot-ids " + " ".join(snapshot_ids) + " --query 'Snapshots[*].{ID:SnapshotId,State:State,StartTime:StartTime,VolumeId:VolumeId,Progress:Progress}' --output table")

if __name__ == "__main__":
    main()
