class Mode:
    car_hunt = "CAR HUNT"
    world_series = "WORLD SERIES"
    limited_series = "LIMITED SERIES"
    trial_series = "TRIAL SERIES"


class TaskName:
    car_hunt = "car_hunt"
    world_series = "world_series"
    other_series = "other_series"
    free_pack = "free_pack"


class TaskStatus:
    default = ""
    start = "start"
    done = "done"


ModeTaskMapping = {
    Mode.car_hunt: TaskName.car_hunt,
    Mode.world_series: TaskName.world_series,
    Mode.limited_series: TaskName.other_series,
    Mode.trial_series: TaskName.other_series,
}
