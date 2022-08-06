import aws_cdk as core
import aws_cdk.assertions as assertions

from wordpress.wordpress_stack import WordpressStack

# example tests. To run these tests, uncomment this file along with the example
# resource in wordpress/wordpress_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = WordpressStack(app, "wordpress")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
