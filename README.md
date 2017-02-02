# jungle-explorer

## Name
I had to call it something.  \*shrug\*

## Purpose
Micro service to return information about EC2 Auto Scaling groups and their Launch Configs.

It's more of a record of the author's exploration of the AWS API than anything else.  If this was to be used in anger, I'd like to make it a little less crude and not rely on things like user_data to launch the service.  If the launch and the app weren't baked into the AMI itself, we'd have to account for start/stop/restart of the service without nuking the instance entirely.

## Installation

    git clone git@github.com:nikogura/jungle-explorer.git
    
    pip install -e jungle-explorer
    
    
    
    
## Usage

kk

##  Access
Access is via http on port 5000  