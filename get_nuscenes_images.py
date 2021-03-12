# We implemented our method on top of AB3DMOT's KITTI tracking open-source code

from __future__ import print_function
import os.path, copy, numpy as np, time, sys
from numba import jit
from sklearn.utils.linear_assignment_ import linear_assignment
from filterpy.kalman import KalmanFilter
from utils import load_list_from_folder, fileparts, mkdir_if_missing
from scipy.spatial import ConvexHull
from covariance import Covariance
import json
from nuscenes import NuScenes
from nuscenes.eval.common.data_classes import EvalBoxes
from nuscenes.eval.tracking.data_classes import TrackingBox 
from nuscenes.eval.detection.data_classes import DetectionBox 
from pyquaternion import Quaternion
from tqdm import tqdm

'''Modellled after main.py'''

def test(data_split, covariance_id, match_distance, match_threshold, match_algorithm, save_root, use_angular_velocity):
  '''
  submission {
    "meta": {
        "use_camera":   <bool>  -- Whether this submission uses camera data as an input.
        "use_lidar":    <bool>  -- Whether this submission uses lidar data as an input.
        "use_radar":    <bool>  -- Whether this submission uses radar data as an input.
        "use_map":      <bool>  -- Whether this submission uses map data as an input.
        "use_external": <bool>  -- Whether this submission uses external data as an input.
    },
    "results": {
        sample_token <str>: List[sample_result] -- Maps each sample_token to a list of sample_results.
    }
  }

  '''
  save_dir = os.path.join(save_root, data_split); mkdir_if_missing(save_dir)
  if 'train' in data_split:
    detection_file = '/cs231a/data/nuscenes_new/megvii_train.json'
    data_root = '/cs231a/data/nuscenes/trainval'
    version='v1.0-trainval'
    output_path = os.path.join(save_dir, 'results_train_probabilistic_tracking.json')
  elif 'val' in data_split:
    detection_file = '/cs231a/data/nuscenes_new/megvii_val.json'
    data_root = '/cs231a/data/nuscenes/trainval'
    version='v1.0-trainval'
    output_path = os.path.join(save_dir, 'results_val_probabilistic_tracking.json')
  elif 'test' in data_split:
    detection_file = '/cs231a/data/nuscenes_new/megvii_test.json'
    data_root = '/cs231a/data/nuscenes/test'
    version='v1.0-test'
    output_path = os.path.join(save_dir, 'results_test_probabilistic_tracking.json')

  nusc = NuScenes(version=version, dataroot=data_root, verbose=True)

  total_frames = 0

  with open(detection_file) as f:
    data = json.load(f)
  assert 'results' in data, 'Error: No field `results` in result file. Please note that the result format changed.' \
    'See https://www.nuscenes.org/object-detection for more information.'

  all_results = EvalBoxes.deserialize(data['results'], DetectionBox)
  meta = data['meta']
  print('meta: ', meta)
  print("Loaded results from {}. Found detections for {} samples."
    .format(detection_file, len(all_results.sample_tokens)))

  processed_scene_tokens = set()
  for sample_token_idx in range(10))):
    sample_token = all_results.sample_tokens[sample_token_idx]
    scene_token = nusc.get('sample', sample_token)['scene_token']
    if scene_token in processed_scene_tokens:
      continue
    first_sample_token = nusc.get('scene', scene_token)['first_sample_token']
    current_sample_token = first_sample_token

    data_path, box_list, cam_intrinic = nuc.get_sample_dat(current_sample_token)
    data = Image.open(data_path)
    total_frames += 1

      # get next frame and continue the while loop
    current_sample_token = nusc.get('sample', current_sample_token)['next']

      # left while loop and mark this scene as processed
    processed_scene_tokens.add(scene_token)

    # finished tracking all scenes, write output data
  output_data = {'meta': meta, 'results': results}
  with open(output_path, 'w') as outfile:
    json.dump(output_data, outfile)

  print("Total Tracking %d frames"%(total_frames))


def main():
  if len(sys.argv)!=9:
    print("Usage: python main.py data_split(train, val, test) covariance_id(0, 1, 2) match_distance(iou or m) match_threshold match_algorithm(greedy or h) use_angular_velocity(true or false) dataset save_root")
    sys.exit(1)

  data_split = sys.argv[1]
  covariance_id = int(sys.argv[2])
  match_distance = sys.argv[3]
  match_threshold = float(sys.argv[4])
  match_algorithm = sys.argv[5]
  use_angular_velocity = sys.argv[6] == 'True' or sys.argv[6] == 'true'
  dataset = sys.argv[7]
  save_root = os.path.join('./' + sys.argv[8])

  if dataset == 'kitti':
    print('track kitti not supported')
  elif dataset == 'nuscenes':
    print('track nuscenes')
    track_nuscenes(data_split, covariance_id, match_distance, match_threshold, match_algorithm, save_root, use_angular_velocity)
  elif dataset == 'nuscenes':
    print('test')
    test(data_split, covariance_id, match_distance, match_threshold, match_algorithm, save_root, use_angular_velocity)

if __name__ == '__main__':
    main()
