import yaml

with open("custom.yaml") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

print(config["任务"])

flat_task = []

def parse_task(tasks, flat_task):
    for task in tasks:
        if "组" in task:
            sub_tasks = []
            for sub_task in task["组"]:
                sub_tasks += [sub_task["名称"]] * sub_task["次数"]
            flat_task += sub_tasks * task["次数"]
        else:
            flat_task += [task["名称"]] * task["次数"]

parse_task(config["任务"], flat_task)
print(flat_task)
