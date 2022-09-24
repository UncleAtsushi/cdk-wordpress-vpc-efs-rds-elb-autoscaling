1. Deploy Network Stack

# cdk deploy Network


2. Deploy Storage Stack

# cdk deploy Storage


3. Deploy Database Stack

# cdk deploy Database


4. Deploy Computing Stack

# cdk deploy Computing


5. Create Custum AMI by Single EC2 deployed


5. Modify Computing Stack code(Computing_stack.py)
	Commnet out line below.
	65-71
	83-86
	92-105
	168-169

	Delete Comment out lines below.
	88-90
	And Set the AMI ID you created.
	
	machine_image=ec2.MachineImage.generic_linux(
            {"us-east-1": "ami-XXXXXXXXXXXXXXXXXX"}
	)

7. Deploy Computing stack again.
