# EC2 Instance Setup with Terraform

Assignment for DevOps position - Voyager Labs

## Task 1 - Terraform

1. Created 2 ssh keys: main and dev

2. Stored the dev key as an AWS secret

3. Created 2 ec2 instances with init script for basic configuration using terraform

4. Created a role and policy to access the secret from the instance

5. **Verify SSH Access**
   - Connected to the instance as the `dev` user using the private key:
     ```bash
     ssh -i ~/Downloads/dev-user-ssh-key.pem dev@52.28.66.120
     ```

## Troubleshooting
- Check `cloud-init` logs on the instance:
  ```bash
  sudo cat /var/log/cloud-init-output.log


## Task 2 - Ansible

1. Created an Ansible playbook that uses hosts.ini and installs the following in the instance:
- google-chrome-stable
- bzip2
- perl

```
ssh -i ~/Downloads/main-key.pem dev@63.176.81.240
```

2. Added backup and updated the host entries
3. Useful commands:
```
  ansible-playbook -i hosts.ini playbook.yml

  aws ec2 describe-instances --filters "Name=tag:Name,Values=DevOpsInstance-1,DevOpsInstance-2"

  aws ec2 describe-instances --instance-ids i-0e813accd77de25ee --query "Reservations[*].Instances[*].{ID:InstanceId,Volumes:BlockDeviceMappings[*].Ebs.VolumeId,State:State.Name}" --output table
```

## Task 3 - Scripting

Created a python script that
1. Retrieve all volume IDs attached to a specific instance.
2. Create a snapshot for a specified volume
3. Create snapshots for all volumes attached to an instance and delete older ones.
4. run the script as: python3 ebs_snapshot.py <snapshot_name> <instance_id> <number_of_snapshots_to_keep>

```
python3 ebs_snapshot.py "my_snapshot" i-0283242755e101371 3
```
5. test
```
    print("aws ec2 describe-snapshots --snapshot-ids " + " ".join(snapshot_ids) + " --query 'Snapshots[*].{ID:SnapshotId,State:State,StartTime:StartTime,VolumeId:VolumeId,Progress:Progress}' --output table")

```

## Task 4 - Kubernetes

1. I decided to go with k3d installation approach 
2. Created a bash script that:
- Installs and enables docker
- Installs k3d and creates a cluster
- Created a simple Appache deployment with a NodePort service for debug

3. Accress the apache server via curl

```
curl http://localhost:30252

curl http://63.176.81.240:30252

```