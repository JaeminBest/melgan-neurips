import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from mel2wav import MelVocoder

from pathlib import Path
from tqdm import tqdm
import argparse
import json
import librosa
import shutil
import torch

from utils.credential import s3


def span_path(args,full_filepath):
  parse_speaker_id = full_filepath.split('/')[-4].split('-')[-1]
  parse_file_id = full_filepath.split('/')[-3].split('-')[-1]
  parse_filename = full_filepath.split('/')[-1]
  new_path = args.folder / "{}-{}-{}".format(parse_speaker_id,parse_file_id,parse_filename)
  os.system('mv {} {}'.format(str(full_filepath),new_path))
  return new_path


def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument("--folder", type=Path, required=True)
  parser.add_argument("--data-list-path", type=Path, required=True)
  parser.add_argument("--data-param-path", type=Path, default='/app/params.json')
  parser.add_argument('-d', action='store_true')
  args = parser.parse_args()
  return args



def main():
  args = parse_args()
  
  args.folder.mkdir(exist_ok=True, parents=True)
  
  # json load
  with open(args.data_param_path) as f:
    json_data = json.load(f)
  data_list = json_data['data']
  
  if os.path.isfile(args.data_list_path):
    os.remove(args.data_list_path)
  
  f = open(args.data_list_path,'a')
  
  # download from s3
  if not args.d:
    for data in data_list:
      parse_id = int(data.split('-')[-1])
      parse_type = data.split('-')[0]
      if parse_type=='nltk':
        dirpath = str(args.folder) / Path('speaker-{}'.format(parse_id))
        os.makedirs(str(dirpath),exist_ok=True)
        os.system("aws s3 cp s3://mindlogic-tts-cache/nltk/speaker-{}/ {} --recursive".format(parse_id,os.path.join(*dirpath.parts)))
      else:
        dirpath = args.folder/Path('speaker-{}'.format(parse_id))
        os.makedirs(str(dirpath),exist_ok=True)
        os.system("aws s3 cp s3://mindlogic-tts-cache/celeb/speaker-{} {} --recursive".format(parse_id,os.path.join(*dirpath.parts)))
    
    # rearrange to structure
    print("rearrange start",flush=True)
    for rootpath,dirs,files in os.walk(str(args.folder)):
      for file in files:
        filepath = os.path.join(rootpath,file)
        new_path = span_path(args,filepath)
        print(new_path,flush=True)
        f.write(new_path+'\n')
    
  print("dummy clean start",flush=True)
  # delete dummy directory
  for data in data_list:
    parse_id = int(data.split('-')[-1])
    parse_type = data.split('-')[0]
    dirpath = os.path.join(args.folder,'speaker-{}'.format(parse_id))
    if os.path.isdir(dirpath):
      shutil.rmtree(dirpath)
  
  print("finished",flush=True)
  f.close()
  

if __name__ == "__main__":
  main()

