import os

def getSlides(resource_dir: str) -> dict:
    src = lambda file: os.path.join(resource_dir, file)

    return {
        "INTRODUCTION": [src("preparation.png"), src("overview.png")],

        "TUTORIAL": [src("tutorial.png")],
        "TUTORIAL_REACHING": [src("tutorial_reaching.png")],
        "TUTORIAL_AVOIDING": [src("tutorial_avoiding.png")],

        "PRETEST_REACHING1": [src("pre_reaching1.png"), src("tutorial_avoiding.png")],
        "PRETEST_REACHING2": [src("pre_reaching2.png"), src("tutorial_reaching.png")],

        "TRAINING_REACHING": [src("train_reaching.png")],

        "POSTTEST_REACHING1": [src("post_reaching1.png")],
        "RECAP_REACHING": [src("recap_reaching.png")],
        "POSTTEST_REACHING2": [src("post_reaching2.png")],

        "PRETEST_AVOIDING1": [src("pre_avoiding1.png"), src("tutorial_reaching.png")],
        "PRETEST_AVOIDING2": [src("pre_avoiding2.png"), src("tutorial_avoiding.png")],

        "TRAINING_AVOIDING": [src("train_avoiding.png")],

        "POSTTEST_AVOIDING1": [src("post_avoiding1.png")],
        "RECAP_AVOIDING": [src("recap_avoiding.png")],
        "POSTTEST_AVOIDING2": [src("post_avoiding2.png")],

        "BREAK": [src("break.png")]
    }