# jungle-explorer

## Name
I had to call it something.  \*shrug\*

## Build Status: [![CircleCI](https://circleci.com/gh/nikogura/jungle-explorer.svg?style=svg)](https://circleci.com/gh/nikogura/jungle-explorer)

## Purpose
Micro service to return information about EC2 Auto Scaling groups and their Launch Configs.

It's more of a record of the author's exploration of the AWS API than anything else.  If this was to be used in anger, I'd like to make it a little less crude and not rely on things like user_data to launch the service.  If the launch and the app weren't baked into the AMI itself, we'd have to account for start/stop/restart of the service without nuking the instance entirely.

## Installation

    git clone git@github.com:nikogura/jungle-explorer.git
    
    pip install -e jungle-explorer
    
### Configuration
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

* *flavor* The name of the size/power/base config of VM to create.

* *test_key_name* The name of the SSH Key in AWS

* *test_key_file_name* The name of the SSH Key file stored locally

* *requirements_url* The URL for the requirements file for running this script

* *script_url* The URL location of jungle.py

* *deploy_tag* The tag linking the Autoscaling Group to the Launch Config
    
## Usage

### Status

    python jungle.py 
    
### Create Service

    python jungle.py -a create
    
Output will display the url that the service can be reached on
    
### Destroy Service

    python jungle.py -a destroy

##  Access
Access is via http on port 5000 such as:

    curl -i ec2-54-193-12-243.us-west-1.compute.amazonaws.com:5000