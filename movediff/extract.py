"""Step 1: video -> per-frame MediaPipe Pose landmarks, saved as .npz.

Output arrays (T = frames):
  xy     (T, 33, 2)  image position in pixels, y pointing UP
  z      (T, 33)     MediaPipe's relative depth, same scale as x (noisy)
  vis    (T, 33)     landmark visibility in [0, 1]
  world  (T, 33, 3)  MediaPipe world landmarks in metres, hip-centred (noisy depth)
  t      (T,)        frame time in seconds
Frames with no detected person are NaN.
"""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

import numpy as np

from .landmarks import SKELETON

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL = ROOT / "models" / "pose_landmarker_full.task"
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
    "pose_landmarker_full/float16/latest/pose_landmarker_full.task"
)


def ensure_model(path: Path) -> Path:
    path = Path(path)
    if path.exists():
        return path
    if path != DEFAULT_MODEL:
        raise SystemExit(f"model file not found: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    print(f"downloading pose model to {path}", file=sys.stderr)
    tmp = path.with_suffix(".part")
    urllib.request.urlretrieve(MODEL_URL, tmp)
    tmp.rename(path)
    return path


def extract(video: Path, out: Path, model: Path = DEFAULT_MODEL, overlay: Path | None = None) -> Path:
    import cv2
    import mediapipe as mp
    from mediapipe.tasks.python import vision
    from mediapipe.tasks.python.core.base_options import BaseOptions

    model = ensure_model(model)
    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise SystemExit(f"cannot open video: {video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    n_total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    options = vision.PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(model)),
        running_mode=vision.RunningMode.VIDEO,
        num_poses=1,
    )

    xy, z, vis, world, times = [], [], [], [], []
    writer = None
    width = height = 0
    last_ms = -1
    with vision.PoseLandmarker.create_from_options(options) as landmarker:
        i = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            height, width = frame.shape[:2]
            t_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
            if not np.isfinite(t_ms) or (i > 0 and t_ms <= 0):
                t_ms = i * 1000.0 / fps
            ms = max(int(round(t_ms)), last_ms + 1)  # MediaPipe needs strictly increasing timestamps
            last_ms = ms

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = landmarker.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), ms)

            if result.pose_landmarks:
                pts = result.pose_landmarks[0]
                wpts = result.pose_world_landmarks[0]
                f_xy = np.array([[p.x * width, (1.0 - p.y) * height] for p in pts])
                f_z = np.array([p.z * width for p in pts])
                f_vis = np.array([p.visibility if p.visibility is not None else np.nan for p in pts])
                f_world = np.array([[p.x, p.y, p.z] for p in wpts])
            else:
                f_xy = np.full((33, 2), np.nan)
                f_z = np.full(33, np.nan)
                f_vis = np.zeros(33)
                f_world = np.full((33, 3), np.nan)
            xy.append(f_xy)
            z.append(f_z)
            vis.append(f_vis)
            world.append(f_world)
            times.append(ms / 1000.0)

            if overlay is not None:
                if writer is None:
                    Path(overlay).parent.mkdir(parents=True, exist_ok=True)
                    writer = cv2.VideoWriter(str(overlay), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
                writer.write(_draw(frame, f_xy, f_vis, height))

            i += 1
            if i % 100 == 0:
                print(f"\r{video.name}: {i}/{n_total} frames", end="", file=sys.stderr)
    print(file=sys.stderr)
    cap.release()
    if writer is not None:
        writer.release()
    if not xy:
        raise SystemExit(f"no frames read from {video}")

    xy_a = np.array(xy)
    detected = ~np.isnan(xy_a[:, 0, 0])
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        out,
        xy=xy_a,
        z=np.array(z),
        vis=np.array(vis),
        world=np.array(world),
        t=np.array(times),
        fps=fps,
        width=width,
        height=height,
        video=str(video),
    )
    print(f"{video.name}: {len(xy)} frames, person found in {detected.mean():.0%}, saved {out}")
    return out


def _draw(frame, f_xy, f_vis, height):
    import cv2

    img = frame.copy()
    if np.isnan(f_xy[0, 0]):
        return img
    px = np.column_stack([f_xy[:, 0], height - f_xy[:, 1]]).astype(int)
    for a, b in SKELETON:
        if f_vis[a] > 0.5 and f_vis[b] > 0.5:
            cv2.line(img, tuple(px[a]), tuple(px[b]), (230, 230, 230), 3, cv2.LINE_AA)
    for k in set(sum(SKELETON, ())):
        if f_vis[k] > 0.5:
            cv2.circle(img, tuple(px[k]), 5, (214, 120, 42), -1, cv2.LINE_AA)
    return img
