---
title: Search tensorflow/pytorch cor. cuda and cudann version

tags:
    -linux
    -tex
---

### Tensorflow

See https://www.tensorflow.org/install/source?hl=zh-cn#gpu

### Pytorch

See https://github.com/elenacliu/pytorch_cuda_driver_compatibilities

### Config the cuda and cudnn version in popOS

Install the cuda and cudann via popos as:

1. Check the max version of the gpu driver supported by:

```bash

nvidia-smi
```

If the driver does not support the expected cuda version, then update the driver by:

```
sudo proxychains apt-get install system76-driver-nvidia
```

We can find the package in https://apt-origin.pop-os.org/proprietary

```
sudo proxychains apt install system76-cuda-10.1
sudo proxychains apt install system76-cudnn-10.1
```

or

```
sudo proxychains apt install system76-cuda-11.2
sudo proxychains apt install system76-cudnn-11.2
```

And check the cuda env in `zsh' is like

```
export PATH=/usr/lib/cuda/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=/usr/lib/cuda/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
```

We can switch between each CUDA version with the following command:

```
sudo update-alternatives --config cuda
```

To verify installation, run this command to see the current version of the NVIDIA CUDA compiler:

```
nvcc -V
```

You can check the version of cuDNN with this command:

```
cat /usr/lib/cuda/include/cudnn_version.h | grep CUDNN_MAJOR -A 2     
```
