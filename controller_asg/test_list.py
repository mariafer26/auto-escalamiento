from controller_asg.controller import ControllerASG


controller = ControllerASG()

instances = controller.list_instances()

for instance in instances:
    print(instance)