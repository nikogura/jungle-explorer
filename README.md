# jungle-explorer

## Name
I had to call it something.  \*shrug\*

## Build Status: [![CircleCI](https://circleci.com/gh/nikogura/jungle-explorer.svg?style=svg)](https://circleci.com/gh/nikogura/jungle-explorer)

## Purpose
Micro service to return information about EC2 Auto Scaling groups and their Launch Configs.

It's more of a record of the author's exploration of the AWS API than anything else.  If this was to be used in anger, I'd like to make it a little less crude and not rely on things like user_data to launch the service.  If the launch and the app weren't baked into the AMI itself, we'd have to account for start/stop/restart of the service without nuking the instance entirely.

## Usage

### Clone repo

    git clone git@github.com:nikogura/jungle-explorer.git
    
### CD into the repo

    cd jungle-explorer
    
### Install prereqs.  Either of the following will work:

    pip install -r requirements.txt
    
Or

    pip install -e .
    
    
### Edit the Config with your favorite editor
See 'Configuration Reference' below

    vi jungle.py
    
### Create the Service VMs

    python jungle.py -a create
    
Command will output the hostname of the service.
    
### Provision Service VM
Wait a couple minutes for the VM to wake up.  VM needs to be up, and this takes a couple minutes. 

This will send your secrets to the VM.  This is very crude, for demonstration purposes.

    python jungle.py -a provision
    
Needs better handling, but honestly, this whole secret provisioning system is such a hack that there's no point in polishing a turd. In reality, we'd use a real secret provisioning system like Vault.  This is just a hack.
    
### Use Service
Hit the service any way you please

    curl -i <hostname>:5000
    
    
### Get Status of Service

    python jungle.py 
    

### Destroy Service

    python jungle.py -a destroy

### Configuration Reference
Near the top of 'jungle.py' you'll see some configuration options.  You'll have to modify them for your own usage.  Inside you'll see my defaults.

* *security_group_id*  This is the security group id you're creating instances under (Required to allow access to the service, and the user-data that starts the service) The default in the script is mine.  Your setup will be different.

At a minimum you'll need to enable inbound access on the following:

    22
    5000
    80
    443
    
80 and 443 are needed by the cloud-init feature to enable user_data.  22 is for SSH, and 5000 is the service itself.

* *region* aws region

* *app_name* The service name.  Used to tag instances.  Instances are destroyed via this name, so choose it wisely.

* *image* AMI image for this service to use (must be RH derived)

* *user* User on the VM to run the service as

* *credential_file_name*  The name of your credentials file

* *flavor* The name of the size/power/base config of VM to create.

* *test_key_name* The name of the SSH Key in AWS

* *test_key_file_name* The name of the SSH Key file stored locally

* *requirements_url* The URL for the requirements file for running this script

* *script_url* The URL location of jungle.py

* *deploy_tag* The tag linking the Autoscaling Group to the Launch Config
    
