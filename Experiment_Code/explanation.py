from enum import Enum
class Explanation(Enum):
    INTRODUCTION = ["text_slides/preparation.JPG", "text_slides/overview.JPG"]

    TUTORIAL = ["text_slides/tutorial.JPG"]
    TUTORIAL_REACHING = ["text_slides/tutorial_reaching.JPG"]
    TUTORIAL_AVOIDING = ["text_slides/tutorial_avoiding.JPG"]

    PRETEST_REACHING1 = ["text_slides/pre_reaching1.JPG"]
    PRETEST_REACHING2 = ["text_slides/pre_reaching2.JPG"]

    TRAINING_REACHING = ["text_slides/train_reaching.JPG"]

    POSTTEST_REACHING1 = ["text_slides/post_reaching1.png"]
    RECAP_REACHING = ["text_slides/recap_reaching.png"]
    POSTTEST_REACHING2 = ["text_slides/post_reaching2.png"]

    PRETEST_AVOIDING1 = ["text_slides/pre_avoiding1.JPG"]
    PRETEST_AVOIDING2 = ["text_slides/pre_avoiding2.JPG"]

    TRAINING_AVOIDING = ["text_slides/train_avoiding.JPG"]

    POSTTEST_AVOIDING1 = ["text_slides/post_avoiding1.png"]
    RECAP_AVOIDING = ["text_slides/recap_avoiding.png"]
    POSTTEST_AVOIDING2 = ["text_slides/post_avoiding2.png"]

    BREAK = ["text_slides/break.JPG"]