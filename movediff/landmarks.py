"""MediaPipe Pose landmark names and indices (33 points, person-centric left/right)."""

NAMES = (
    "nose",
    "left_eye_inner", "left_eye", "left_eye_outer",
    "right_eye_inner", "right_eye", "right_eye_outer",
    "left_ear", "right_ear",
    "mouth_left", "mouth_right",
    "left_shoulder", "right_shoulder",
    "left_elbow", "right_elbow",
    "left_wrist", "right_wrist",
    "left_pinky", "right_pinky",
    "left_index", "right_index",
    "left_thumb", "right_thumb",
    "left_hip", "right_hip",
    "left_knee", "right_knee",
    "left_ankle", "right_ankle",
    "left_heel", "right_heel",
    "left_foot_index", "right_foot_index",
)
INDEX = {name: i for i, name in enumerate(NAMES)}

# Lines drawn on the overlay video.
SKELETON = (
    (11, 12), (11, 23), (12, 24), (23, 24),
    (11, 13), (13, 15), (15, 19),
    (12, 14), (14, 16), (16, 20),
)


def lm(side: str, joint: str) -> int:
    """Index of `joint` on `side` ('left' or 'right'). 'nose' ignores side."""
    if joint == "nose":
        return 0
    key = f"{side}_{joint}"
    if key not in INDEX:
        raise ValueError(f"unknown landmark {key!r}")
    return INDEX[key]
