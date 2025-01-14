import numpy as np
import cv2,os,sys

caffe_root = '../'
os.chdir(caffe_root)
sys.path.insert(0, 'python')
import caffe
caffe.set_device(0)
caffe.set_mode_gpu()
model_def = 'models/faceboxes/deploy.prototxt'
model_weights = 'models/faceboxes/faceboxes.caffemodel'
net = caffe.Net(model_def, model_weights, caffe.TEST)

count = 0
Path = '/dev/ftian_disk/tianfei01/workspace/deeplearn/traindata/detect/face/wider_face/mmdetect_wider_val/images/'
f = open('./test/widerface_val_dets.txt', 'wt')
for Name in open('/dev/ftian_disk/tianfei01/workspace/deeplearn/traindata/detect/face/wider_face/mmdetect_wider_val/images/image.list'):
    Image_Path = Path + Name.rstrip()
    image = caffe.io.load_image(Image_Path)
    im_scale = 1.0
    if im_scale != 1:
        image = cv2.resize(image, None, None, fx=im_scale, fy=im_scale, interpolation=cv2.INTER_LINEAR)
    net.blobs['data'].reshape(1, 3, image.shape[0], image.shape[1])
    transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
    transformer.set_transpose('data', (2, 0, 1))
    transformer.set_mean('data', np.array([104, 117, 123])) # mean pixel
    transformer.set_raw_scale('data', 255)  # the reference model operates on images in [0,255] range instead of [0,1]
    transformer.set_channel_swap('data', (2, 1, 0))  # the reference model has channels in BGR order instead of RGB
    transformed_image = transformer.preprocess('data', image)
    net.blobs['data'].data[...] = transformed_image

    detections = net.forward()['detection_out']
    det_label = detections[0, 0, :, 1]
    det_conf = detections[0, 0, :, 2]
    det_xmin = detections[0, 0, :, 3]
    det_ymin = detections[0, 0, :, 4]
    det_xmax = detections[0, 0, :, 5]
    det_ymax = detections[0, 0, :, 6]

    for i in xrange(det_conf.shape[0]):
        xmin = int(round(det_xmin[i] * image.shape[1]))
        ymin = int(round(det_ymin[i] * image.shape[0]))
        xmax = int(round(det_xmax[i] * image.shape[1]))
        ymax = int(round(det_ymax[i] * image.shape[0]))
        ymin += 0.2 * (ymax - ymin + 1)
        score = det_conf[i]
        f.write('{:s} {:.3f} {:.1f} {:.1f} {:.1f} {:.1f}\n'.
                format(Name[:-1], score, xmin/im_scale, ymin/im_scale, xmax/im_scale, ymax/im_scale))
    count += 1
    print('%d' % count)
