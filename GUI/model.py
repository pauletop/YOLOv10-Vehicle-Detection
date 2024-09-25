from ultralytics import YOLO
import cv2
import numpy as np
import torchvision.io as tio

class YOLOModel:
  def __init__(self, model_path='./runs/detect/train6/weights/best.pt', task='detect'):
    self.model = YOLO(model_path, task=task)
    self.rgb_colors = [(252, 165, 165), (45, 212, 191), (132, 204, 22), (14, 165, 233), (251, 113, 113)] 
    self.names = self.model.names
    self.video_codec = 'h264' # supported by browsers
  
  def predict(self, path):
    results = self.model(path)
    return results
  
  def draw_boxes(self, results):
    frames = []
    is_valid = False
    for result in results:
      ori_img = cv2.cvtColor(result.orig_img, cv2.COLOR_BGR2RGB).copy()
      h, _, _ = ori_img.shape # for test image: (1620, 2880, 3)
      # fontscale and thickness depend on the resolution of the input image
      font_scale = 5 * h // 1620
      thickness = 3 * h // 1620
      
      boxes = result.boxes
      draw_data = sorted(zip(boxes.xyxy.cpu().numpy(), boxes.cls.cpu().numpy(), boxes.conf.cpu().numpy()), key=lambda x: x[2])
      if len(draw_data) > 0:
        is_valid = True
      carr = [0]*len(self.names)
      for i, (box, cat, prb) in enumerate(draw_data):
        cat = int(cat)
        carr[cat] += 1
        c1, c2 = (int(box[0]), int(box[1])), (int(box[2]), int(box[3]))
        cv2.rectangle(ori_img, c1, c2, self.rgb_colors[cat], 3)
        label = f'{self.names[int(cat)]} {prb:.2f}'
        t_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_PLAIN, font_scale , thickness)[0]
        c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
        cv2.rectangle(ori_img, c1, c2, self.rgb_colors[cat], -1)
        cv2.putText(ori_img, label, (c1[0], c1[1] - 2), cv2.FONT_HERSHEY_PLAIN, font_scale, [225,255,255], thickness)
      summary = f'Total: {len(draw_data):02d} - ' + \
      ';'.join([f'{self.names[i]}: {carr[i]}' for i in range(len(self.names)) if carr[i] > 0])
      cv2.putText(ori_img, summary, (20, 30), cv2.FONT_HERSHEY_PLAIN, 2, self.rgb_colors[4], thickness)
            
      frames.append(ori_img)
    return np.array(frames), is_valid
  
  def save_frames(self, frames, path2fileOut, fps=30):
    if path2fileOut.endswith('.mp4'):
      tio.write_video(path2fileOut, frames, fps=fps, video_codec=self.video_codec)
    elif path2fileOut.endswith('.jpg'):
      img = cv2.cvtColor(frames[0], cv2.COLOR_BGR2RGB)
      cv2.imwrite(path2fileOut, img)
      
    # GUI/static/predictions/... -> static/predictions/...
    return path2fileOut.split('/', 1)[1]
  
  def process(self, path2fileIn, path2fileOut):
    results = self.predict(path2fileIn)
    frames, is_val = self.draw_boxes(results)
    return self.save_frames(frames, path2fileOut), is_val