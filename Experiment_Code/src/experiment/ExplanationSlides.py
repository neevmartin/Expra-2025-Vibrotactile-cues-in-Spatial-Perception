import os

def getSlides(resource_dir: str) -> dict:
    src = lambda file: os.path.join(resource_dir, file)

    return {
        "INTRODUCTION": [src("preparation.JPG"), src("overview.JPG")],

        "TUTORIAL": [src("tutorial.JPG")],
        "TUTORIAL_REACHING": [src("tutorial_reaching.JPG")],
        "TUTORIAL_AVOIDING": [src("tutorial_avoiding.JPG")],

        "PRETEST_REACHING1": [src("pre_reaching1.JPG")],
        "PRETEST_REACHING2": [src("pre_reaching2.JPG")],

        "TRAINING_REACHING": [src("train_reaching.JPG")],

        "POSTTEST_REACHING1": [src("post_reaching1.png")],
        "RECAP_REACHING": [src("recap_reaching.png")],
        "POSTTEST_REACHING2": ["post_reaching2.png"],

        "PRETEST_AVOIDING1": [src("pre_avoiding1.JPG")],
        "PRETEST_AVOIDING2": [src("pre_avoiding2.JPG")],

        "TRAINING_AVOIDING": [src("train_avoiding.JPG")],

        "POSTTEST_AVOIDING1": [src("post_avoiding1.png")],
        "RECAP_AVOIDING": [src("recap_avoiding.png")],
        "POSTTEST_AVOIDING2": [src("post_avoiding2.png")],

        "BREAK": [src("break.JPG")]
    }