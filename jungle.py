import sys
import boto3
import getopt

from flask import Flask

app_name = 'jungle'
region = 'us-west-1'
image = 'ami-af4333cf'
user = 'centos'
flavor = 't2.micro'
test_key_name = 'TestKey'
test_key_file_name = 'TestKey.pem'
security_group_id = 'sg-3f238d58'
requirements_url = ''
script_url = ''

app = Flask(app_name)

user_data = """#!/bin/bash
sudo yum install -y epel-release

sudo yum install -y python2-pip

wget -O /tmp/requirements.txt %s

sudo pip install -y /tmp/requirements.txt

wget -O /tmp/jungle.py %s

python /tmp/jungle.py -a service

""" % (requirements_url, script_url)  #really crude, I know

ec2 = boto3.resource('ec2', region_name=region)


@app.route('/')
def hello_world():
    return 'Hello World'


def init():
    key_pair = ec2.KeyPair(test_key_name)

    try:
        if key_pair.key_fingerprint:
            print "Key '%s' already generated.  Movin on." % test_key_name

    except:
        with open(test_key_file_name, 'w') as f:
            key_pair = ec2.create_key_pair(KeyName=test_key_name)
            f.write(str(key_pair.key_material))

        print "Key Created and saved to "+ test_key_file_name


def destroy():
    for instance in ec2.instances.all():
        instance.terminate()


def stop():
    # stop the vm's?  stop the services?
    pass


def start():
    # start the vm's?  start the services?
    pass


def test_user_data():
    with open('user_data', 'w') as f:
        f.write(user_data)

def create():
    instances = ec2.create_instances(
        ImageId=image,
        MinCount=1,
        MaxCount=2,
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


def status():
    print "Status:"
    for instance in ec2.instances.all():
        app_tag = ''
        for tag in instance.tags:
            if tag['Key'] == 'app':
                app_tag = tag['Value']
        print instance.id, instance.instance_type, app_tag


def help_message():
    print "jungle.py -a <action> [init|start|stop|create|destroy|nike|service]"

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
        elif action == 'start':
            start()
        elif action == 'stop':
            stop()
        elif action == 'destroy':
            destroy()
        elif action == 'service':
            app.run()
        elif action == 'test_user_data':
            test_user_data()
        elif action == 'nike':
            print("You chose 'nike', so I'll Just Do It.")
            init()
            create()
            # start()
        else:
            status()

    except getopt.GetoptError:
        help_message()
        sys.exit(2)

# end