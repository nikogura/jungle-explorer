#! /usr/bin/env python

# ***************************************  Start User Config ******************************
# security group id you're creating instances under (Required to allow access to the service, and the user-data that starts the service)
security_group_id = 'sg-3f238d58'

# aws region
region = 'us-west-1'

# app name.  Used to tag instances.  Instances are destroyed via this name, so choose it wisely.
app_name = 'jungle'

#image for this service to use (must be RH derived)
image = 'ami-af4333cf'

# user on the service VM
user = 'centos'

# local credentials file name
credential_file_name = 'credentials'

# size of box to create
flavor = 't2.micro'

# name of the SSH Key in AWS
test_key_name = 'JungleKey'

# name of the SSH Key file stored locally
test_key_file_name = 'JungleKey.pem'

# requirements file for running this script
requirements_url = 'https://github.com/nikogura/jungle-explorer/raw/master/requirements.txt'

# Where to find this script
script_url = 'https://github.com/nikogura/jungle-explorer/raw/master/jungle.py'

# The tag linking the Autoscaling Group to the Launch Config
deploy_tag = 'deploymentName'

# ************************** End User Config ***************************************

import sys
import os
import boto3
import getopt
import json
from flask import Flask
import logging
from logging.handlers import RotatingFileHandler
import subprocess
import time

app = Flask(app_name)
'''
    Call this the "poor man's config management"  Starts the service when the VM boots
'''
user_data = """#!/bin/bash
yum install -y epel-release wget

yum install -y python2-pip

wget -O /tmp/requirements.txt %s

pip install -r /tmp/requirements.txt

wget -O /tmp/jungle.py %s

runuser -l -c "python /tmp/jungle.py -a service" %s

""" % (requirements_url, script_url, user)

filters = [{
    'Name': 'tag:app',
    'Values': [app_name]
}]

ec2 = boto3.resource('ec2', region_name=region)


@app.route('/')
def hello_world():
    '''
    The main route of the service
    :return: json representation of the autoscaling information
    '''
    return json.dumps(autoscaling_info())


def init():
    '''
    Initializes key pairs if needed
    :return: none.  Writes Private key PEM to cwd() if it has to generate a key
    '''
    key_pair = ec2.KeyPair(test_key_name)

    try:
        if key_pair.key_fingerprint:
            print "Key '%s' already generated.  Movin on." % test_key_name

    except:
        with open(test_key_file_name, 'w') as f:
            key_pair = ec2.create_key_pair(KeyName=test_key_name)
            os.chmod(test_key_file_name, 0o600)
            f.write(str(key_pair.key_material))

        print "Key Created and saved to "+ test_key_file_name


def destroy():
    '''
    Destroys jungle vm's in AWS. Specifically destroys VM's with the tag 'app' set to 'jungle'
    :return: none
    '''
    for instance in ec2.instances.filter(Filters=filters):
        instance.terminate()


def test_user_data():
    '''
    Dumps out the 'user data' used to launch images in AWS
    :return: no return value.  Writes sample file to cwd()
    '''
    with open('user_data', 'w') as f:
        f.write(user_data)

def create():
    '''
    Creates the Jungle service in AWS
    :return: none
    '''
    instances = ec2.create_instances(
        ImageId=image,
        MinCount=1,
        MaxCount=1,
        KeyName=test_key_name,
        InstanceType=flavor,
        UserData=user_data,
        SecurityGroupIds=[security_group_id]
    )

    print "Instances created:"
    for instance in instances:
        instance.create_tags(
            DryRun=False,
            Tags=[
                {
                    'Key': 'app',
                    'Value': app_name
                },
            ]
        )
        print(instance.id, instance.instance_type, instance.tags)
        print "Running on %s:5000" % instance.public_dns_name


def provision_secrets():
    for instance in ec2.instances.filter(Filters=filters):
        if instance.state.get('Name') == 'terminated':
            next
        elif instance.state.get('Name') == 'shutting-down':
            next
        elif instance.state.get('Name') == 'running':
            print "Crudely Provisioning Secrets.  In reality we'd use a proper secrets manager."

            cmd1 = ['ssh', '-o', 'StrictHostKeyChecking=no', '-i', test_key_file_name, '%s@%s' % (user, instance.public_dns_name), 'mkdir', '-p', '.aws']
            cmd2 = ['scp', '-i', test_key_file_name,  credential_file_name, '%s@%s:.aws/credentials' % (user, instance.public_dns_name)]

            subprocess.call(cmd1)
            subprocess.call(cmd2)

        else:
            print "Instance not fully up yet.  Try again in a few seconds.  Sorry."


def autoscaling_info():
    '''
    queries informaiton from Autoscaling Groups in AWS
    :return: list of dict containing the following:
        `name` - the name of the deployment  Autoscale Group name + '-' + Launch Group Name
        `ami`    - the amazon machine image id attached to the launch configuration
        `min_instances` - the configured min instances on the auto scaling group
        `max_instances` - the configured max instances on the auto scaling group
    '''

    output = []

    client = boto3.client('autoscaling', region_name=region)

    for group in client.describe_auto_scaling_groups().get('AutoScalingGroups'):
        info = {}
        info['min_instances']  = group.get('MinSize')
        info['max_instances'] = group.get('MaxSize')

        lg_info = launch_group_info()


        for tag in group.get('Tags'):
            if tag.get('Key') == deploy_tag:
                info['name'] = "%s-%s" % (group.get('AutoScalingGroupName'), tag.get('Value'))
                info['ami'] = lg_info.get(tag.get('Value'))

        output.append(info)

    return output

def launch_group_info():
    '''
    queries AWS about configured launch groups.
    :return: dict of {name: ami}  (One big dict, without bothering with pagination.  Could be a problem if you have tons of launch groups.  Then again, do you need that many?)
    '''
    client = boto3.client('autoscaling', region_name=region)

    output = {}

    for config in client.describe_launch_configurations().get('LaunchConfigurations'):
        name = config.get('LaunchConfigurationName')
        ami = config.get('ImageId')

        if name is not None:
            output[name] = ami

    return output


def status():
    '''
    Prints status of 'jungle' service VM's
    :return: none
    '''
    print "Status:        Name | Flavor   | App    | URL"

    for instance in ec2.instances.filter(Filters=filters):
        app_tag = ''
        for tag in instance.tags:
            if tag['Key'] == 'app':
                app_tag = tag['Value']
        if instance.state.get('Name') == 'running':
            print "%s | %s | %s | %s:5000" % (instance.id, instance.instance_type, app_tag, instance.public_dns_name)


def help_message():
    '''
    Prints help message
    :return:
    '''
    print "jungle.py -a <action> [status|create|destroy|service|test_user_data]"

if __name__ == '__main__':
    action = None

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'ha:', ['help','action='])

        for opt, arg in opts:
            if opt == '-h':
                help_message()
                sys.exit()
            elif opt in ("-a", "--action"):
                action = arg

        # embarassingly crude, but this is just a quickie.  I'd prefer a jump table or such.
        if action == 'init':
            init()
        elif action == 'destroy':
            destroy()
        elif action == 'service':
            handler = RotatingFileHandler('/tmp/%s.log' % app_name, maxBytes=10000, backupCount=1)
            handler.setLevel(logging.DEBUG)
            app.logger.addHandler(handler)
            app.run(host='0.0.0.0')
        elif action == 'test_user_data':
            test_user_data()
        elif action == 'ai':
            print autoscaling_info()
        elif action == 'lg':
            print launch_group_info()
        elif action == 'provision':
            provision_secrets()
        elif action == 'create':
            init()
            create()
        else:
            status()

    except getopt.GetoptError:
        help_message()
        sys.exit(2)
